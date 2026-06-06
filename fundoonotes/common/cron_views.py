"""
Cron-triggered endpoint for background tasks.
Called by cron-job.org every minute instead of using a Celery Beat worker.
Protected by a shared secret header so only the cron service can trigger it.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from decouple import config
import hmac

CRON_SECRET = config("CRON_SECRET", default="")


def _get_secret_header(request) -> str:
    """
    Read X-Cron-Secret from the request.
    Django normalises headers to HTTP_X_CRON_SECRET in META,
    but also exposes them via request.headers (case-insensitive).
    """
    # request.headers is case-insensitive in Django 2.2+
    return request.headers.get("X-Cron-Secret", "")


def _is_authorized(request) -> bool:
    if not CRON_SECRET:
        # No secret configured — deny all to avoid accidental open access
        return False
    incoming = _get_secret_header(request)
    if not incoming:
        return False
    return hmac.compare_digest(incoming.strip(), CRON_SECRET.strip())


@csrf_exempt
@require_POST
def trigger_reminders(request):
    """
    POST /api/cron/trigger-reminders/
    Called by cron-job.org every minute.
    Dispatches due note reminders synchronously.
    """
    if not _is_authorized(request):
        return JsonResponse(
            {"error": "Unauthorized", "hint": "Set X-Cron-Secret header matching CRON_SECRET env var"},
            status=401,
        )

    from common.tasks import dispatch_due_reminders
    try:
        dispatch_due_reminders()
        return JsonResponse({"ok": True})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

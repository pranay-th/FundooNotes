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


def _is_authorized(request) -> bool:
    """Check the X-Cron-Secret header matches the configured secret."""
    if not CRON_SECRET:
        return False
    incoming = request.headers.get("X-Cron-Secret", "")
    return hmac.compare_digest(incoming, CRON_SECRET)


@csrf_exempt
@require_POST
def trigger_reminders(request):
    """
    POST /api/cron/trigger-reminders/
    Called by cron-job.org every minute.
    Dispatches due note reminders synchronously.
    """
    if not _is_authorized(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    from common.tasks import dispatch_due_reminders
    try:
        dispatch_due_reminders()
        return JsonResponse({"ok": True})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

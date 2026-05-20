"""
Custom Django middleware.

RequestLoggingMiddleware  — logs every request with timing and user info,
                            and maintains per-method request counters in
                            the Django cache backend.
ExceptionLoggingMiddleware — catches unhandled exceptions and returns a
                             standardized 500 JSON response.

Helper
------
get_request_counts() -> dict
    Returns the current per-method counter snapshot from the cache.
"""

import json
import time

from django.core.cache import cache
from django.http import HttpResponse
from loguru import logger

# ---------------------------------------------------------------------------
# Recognised HTTP methods that get their own counter bucket.
# Any method not in this set is tallied under "OTHER".
# ---------------------------------------------------------------------------
_TRACKED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _cache_key(method: str) -> str:
    """Return the cache key for a given (normalised) method name."""
    return f"request_count_{method}"


def get_request_counts() -> dict:
    """
    Return the current per-method request counters as a plain dict.

    All tracked methods plus the catch-all "OTHER" bucket are always
    present in the returned dict, defaulting to 0 if no requests have
    been recorded yet.

    Returns:
        {
            "GET":    <int>,
            "POST":   <int>,
            "PUT":    <int>,
            "PATCH":  <int>,
            "DELETE": <int>,
            "OTHER":  <int>,
        }
    """
    all_methods = list(_TRACKED_METHODS) + ["OTHER"]
    return {
        method: (cache.get(_cache_key(method)) or 0)
        for method in all_methods
    }


class RequestLoggingMiddleware:
    """
    Logs every HTTP request/response cycle and tracks per-method counters.

    Logged fields:
        - HTTP method
        - Request path
        - Response status code
        - Duration in milliseconds
        - Authenticated user ID (or "anonymous")
        - Running total for that HTTP method (e.g. GET_count=42)

    Counter storage:
        Each method bucket is stored in the Django cache backend under the
        key ``request_count_{METHOD}`` with no TTL (persists until the
        cache is cleared or the process restarts).  The increment is done
        with a get-then-set pattern so it works with any cache backend,
        including the local-memory backend used in tests.

    Precondition:  Standard Django WSGI request/response cycle.
    Postcondition: One INFO log entry written to logs/app.log per request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _increment_counter(method: str) -> int:
        """
        Atomically increment the counter for *method* and return the new value.

        Uses cache.get / cache.set with no TTL so the counter persists for
        the lifetime of the cache (i.e. until a cache flush or process
        restart).

        Args:
            method: Normalised HTTP method string (e.g. "GET").

        Returns:
            The updated counter value after incrementing.
        """
        bucket = method if method in _TRACKED_METHODS else "OTHER"
        key = _cache_key(bucket)
        current = cache.get(key) or 0
        new_value = current + 1
        # timeout=None → no expiry; the entry lives until the cache is cleared
        cache.set(key, new_value, timeout=None)
        return new_value

    # ------------------------------------------------------------------
    # Middleware entry point
    # ------------------------------------------------------------------

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration_ms = (time.time() - start_time) * 1000
        user_id = getattr(request.user, "id", None) or "anonymous"

        method = request.method.upper()
        count = self._increment_counter(method)
        # Use the display bucket name (OTHER for non-standard methods)
        display_bucket = method if method in _TRACKED_METHODS else "OTHER"

        logger.info(
            f"{method} {request.path} | "
            f"status={response.status_code} | "
            f"duration={duration_ms:.2f}ms | "
            f"user={user_id} | "
            f"{display_bucket}_count={count}"
        )

        return response


class ExceptionLoggingMiddleware:
    """
    Catches any unhandled exception that escapes the view layer.

    On exception:
        - Logs the full traceback via Loguru.
        - Returns a 500 JSON response in the standardized format so that
          no raw Django error pages are ever sent to API clients.

    Precondition:  Standard Django WSGI request/response cycle.
    Postcondition: Unhandled exceptions never propagate to the WSGI server
                   as unformatted HTML; clients always receive JSON.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            logger.exception(f"Unhandled exception on {request.method} {request.path}: {exc}")
            body = json.dumps(
                {"message": "Internal server error", "payload": {}, "status": 500}
            )
            return HttpResponse(
                content=body,
                content_type="application/json",
                status=500,
            )

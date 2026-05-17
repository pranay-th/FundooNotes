"""
Custom Django middleware.

RequestLoggingMiddleware  — logs every request with timing and user info.
ExceptionLoggingMiddleware — catches unhandled exceptions and returns a
                             standardized 500 JSON response.
"""

import json
import time

from django.http import HttpResponse
from loguru import logger


class RequestLoggingMiddleware:
    """
    Logs every HTTP request/response cycle.

    Logged fields:
        - HTTP method
        - Request path
        - Response status code
        - Duration in milliseconds
        - Authenticated user ID (or "anonymous")

    Precondition:  Standard Django WSGI request/response cycle.
    Postcondition: One INFO log entry written to logs/app.log per request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration_ms = (time.time() - start_time) * 1000
        user_id = getattr(request.user, "id", None) or "anonymous"

        logger.info(
            f"{request.method} {request.path} | "
            f"status={response.status_code} | "
            f"duration={duration_ms:.2f}ms | "
            f"user={user_id}"
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

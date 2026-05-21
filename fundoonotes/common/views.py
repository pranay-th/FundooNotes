"""
common/views.py — Shared utility views for the fundooNotes API.

Endpoints
---------
GET /api/stats/requests/
    Returns per-method HTTP request counters tracked by
    RequestLoggingMiddleware.  Requires authentication.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.middleware import get_request_counts
from common.response import success_response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def request_stats(request) -> Response:
    """
    GET /api/stats/requests/

    Returns the running per-method request counters maintained by
    ``RequestLoggingMiddleware``.

    Preconditions:
        - Caller must be authenticated (JWT Bearer token required).

    Postconditions:
        - 200: Returns a success_response whose payload contains a dict
               with keys GET, POST, PUT, PATCH, DELETE, OTHER and their
               respective integer counts.

    Example response::

        {
            "message": "Request counts retrieved successfully.",
            "payload": {
                "GET":    42,
                "POST":   10,
                "PUT":     2,
                "PATCH":   1,
                "DELETE":  3,
                "OTHER":   0
            },
            "status": 200
        }
    """
    counts = get_request_counts()
    return Response(
        success_response("Request counts retrieved successfully.", counts),
        status=200,
    )

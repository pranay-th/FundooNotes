"""
Custom DRF exception handler.

Wraps all DRF exception responses in the standardized
{"message": str, "payload": dict, "status": int} format so that
no raw Django error pages are ever returned to API clients.
"""

from loguru import logger
from rest_framework.response import Response
from rest_framework.views import exception_handler

from common.response import error_response


def custom_exception_handler(exc, context) -> Response:
    """
    Drop-in replacement for DRF's default exception handler.

    Behaviour:
        1. Delegates to DRF's built-in handler first.
        2. If DRF produced a response, wraps it in error_response() format
           and logs a WARNING.
        3. If DRF did not handle the exception (unhandled / 500-class),
           logs an ERROR and returns a 500 standardized response.

    Precondition:  exc is any exception raised inside a DRF view.
    Postcondition: The returned Response always has the shape
                   {"message": str, "payload": dict, "status": int}.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # DRF handled it (4xx range) — wrap and log
        view = context.get("view")
        logger.warning(
            f"API exception: {exc.__class__.__name__} | "
            f"view={view.__class__.__name__ if view else 'unknown'} | "
            f"detail={response.data}"
        )
        body = error_response(
            message=str(exc),
            payload=response.data if isinstance(response.data, dict) else {"detail": response.data},
            status_code=response.status_code,
        )
        return Response(body, status=response.status_code)

    # Unhandled exception — log and return 500
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    body = error_response(
        message="Internal server error",
        payload={},
        status_code=500,
    )
    return Response(body, status=500)

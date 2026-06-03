"""
Standardized API response helpers.

All API responses follow the shape:
    {"message": str, "payload": dict, "status": int}
"""


def success_response(message: str, payload: dict, status_code: int = 200) -> dict:
    """
    Build a standardized success response dict.

    Preconditions:
        - message is a non-empty string
        - payload is a dict (may be empty)
        - status_code is a valid 2xx HTTP status integer
    Postconditions:
        - Returns dict with exactly the keys: message, payload, status
    """
    return {
        "message": message,
        "payload": payload,
        "status": status_code,
    }


def error_response(message: str, payload: dict, status_code: int = 400) -> dict:
    """
    Build a standardized error response dict.

    Preconditions:
        - message is a non-empty string
        - payload is a dict (may be empty)
        - status_code is a valid 4xx/5xx HTTP status integer
    Postconditions:
        - Returns dict with exactly the keys: message, payload, status
    """
    return {
        "message": message,
        "payload": payload,
        "status": status_code,
    }

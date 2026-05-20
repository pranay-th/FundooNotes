"""
JWT authentication dependency for the Note Collaboration Service.

The service reuses the same SECRET_KEY and HS256 algorithm as the Django
backend's SimpleJWT configuration, so no separate token exchange is needed.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel

from app.config import settings

# ---------------------------------------------------------------------------
# Bearer scheme
# ---------------------------------------------------------------------------
# HTTPBearer renders a simple "Value" input in Swagger UI — just paste the
# access token you got from Django's /api/users/login/ endpoint.
# No client_id / client_secret fields, because this service never issues
# tokens; it only validates tokens issued by the Django backend.
bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# Token payload model
# ---------------------------------------------------------------------------

class TokenPayload(BaseModel):
    """Represents the decoded, validated contents of a JWT token."""

    user_id: int


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenPayload:
    """
    Decode and validate a Bearer JWT token.

    Raises HTTP 401 for:
    - Missing or malformed token (handled by HTTPBearer)
    - Token payload missing ``user_id``
    - Expired token
    - Any other JWT validation error (bad signature, wrong algorithm, etc.)

    Returns a :class:`TokenPayload` with the authenticated user's ID on success.
    """
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
        return TokenPayload(user_id=user_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials.")

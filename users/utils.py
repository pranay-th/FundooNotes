import uuid
from django.core.cache import cache


def generate_verification_token(user_id: int) -> str:
    """
    Generate a single-use email verification token.
    Stores user_id in Redis under 'verify_{token}' with TTL=3600s.
    Returns the token string.
    """
    token = str(uuid.uuid4())
    cache.set(f"verify_{token}", user_id, timeout=3600)
    return token


def generate_password_reset_token(user_id: int) -> str:
    """
    Generate a single-use password reset token.
    Stores user_id in Redis under 'pwd_reset_{token}' with TTL=3600s.
    Returns the token string.
    """
    token = str(uuid.uuid4())
    cache.set(f"pwd_reset_{token}", user_id, timeout=3600)
    return token

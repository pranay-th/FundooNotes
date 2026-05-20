"""
Business logic for user authentication and account management.

All service functions are called from views and encapsulate the core
domain operations: registration, login, password reset, and email verification.
"""

from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .utils import generate_verification_token, generate_password_reset_token, generate_login_otp
from common.tasks import send_verification_email, send_password_reset_email, send_login_otp_email


def register_user(validated_data: dict) -> User:
    """
    Create a new user account and dispatch a verification email.

    Preconditions:
        - validated_data contains username, email, phone_number, password
        - email and phone_number are unique (enforced by DB constraints)
        - password passes AUTH_PASSWORD_VALIDATORS
    Postconditions:
        - User created with hashed password
        - user.is_verified = False
        - Celery task enqueued to send verification email (non-blocking)

    Args:
        validated_data: Cleaned data from RegisterSerializer.

    Returns:
        The newly created User instance.
    """
    user = User(
        username=validated_data["username"],
        email=validated_data["email"],
        phone_number=validated_data["phone_number"],
        is_verified=False,
    )
    user.set_password(validated_data["password"])
    user.save()

    token = generate_verification_token(user.id)
    send_verification_email.delay(user.email, token)

    return user


def initiate_login(username: str, password: str) -> str:
    """
    Validate credentials and send a login OTP to the user's email.

    Preconditions:
        - username and password are non-empty strings
    Postconditions:
        - OTP stored in Redis under 'login_otp_{user_id}' with TTL=300s
        - Celery task enqueued to send OTP email (non-blocking)
        - Returns the user's email address

    Args:
        username: The user's email (USERNAME_FIELD).
        password: The user's plaintext password.

    Returns:
        The user's email address (so the caller can tell the user where the OTP was sent).

    Raises:
        serializers.ValidationError: On invalid credentials, unverified account,
            or deactivated account.
    """
    user = authenticate(username=username, password=password)

    if user is None:
        raise serializers.ValidationError("Invalid credentials")

    if not user.is_verified:
        raise serializers.ValidationError("Email not verified. Check your inbox.")

    if not user.is_active:
        raise serializers.ValidationError("Account is deactivated.")

    otp = generate_login_otp(user.id)
    send_login_otp_email.delay(user.email, otp)

    return user.email


def verify_login_otp(username: str, otp: str) -> dict:
    """
    Verify the login OTP and return a JWT token pair.

    Preconditions:
        - username is the user's email
        - otp is a 6-digit string
    Postconditions:
        - Returns {"refresh": str, "access": str} on success
        - OTP removed from Redis (single-use enforcement)
        - Raises ValidationError on invalid/expired OTP or unknown user

    Args:
        username: The user's email address.
        otp: The 6-digit OTP from the email.

    Returns:
        Dict with "refresh" and "access" JWT token strings.

    Raises:
        serializers.ValidationError: If the OTP is invalid or expired.
    """
    try:
        user = User.objects.get(email=username)
    except User.DoesNotExist:
        raise serializers.ValidationError("Invalid request.")

    stored_otp = cache.get(f"login_otp_{user.id}")

    if stored_otp is None:
        raise serializers.ValidationError("OTP has expired. Please log in again.")

    if stored_otp != otp:
        raise serializers.ValidationError("Invalid OTP.")

    cache.delete(f"login_otp_{user.id}")

    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def initiate_password_reset(email: str) -> None:
    """
    Trigger a password reset flow for the given email address.

    Silently ignores unknown email addresses to prevent user enumeration.

    Preconditions:
        - email is a valid email format string
    Postconditions:
        - If user exists: reset token stored in Redis, Celery task dispatched
        - If user does not exist: no action taken, no error raised
        - Always returns None

    Args:
        email: The email address to send the reset link to.
    """
    try:
        user = User.objects.get(email=email)
        token = generate_password_reset_token(user.id)
        send_password_reset_email.delay(user.email, token)
    except User.DoesNotExist:
        pass  # Silent fail — no email enumeration


def confirm_password_reset(token: str, new_password: str) -> None:
    """
    Complete a password reset using a valid reset token.

    Preconditions:
        - token is a non-empty string
        - new_password passes AUTH_PASSWORD_VALIDATORS
        - token exists in Redis and has not expired
    Postconditions:
        - user.password updated and hashed
        - token removed from Redis (single-use enforcement)

    Args:
        token: The password reset token from the email link.
        new_password: The new plaintext password to set.

    Raises:
        serializers.ValidationError: If the token is invalid or expired.
    """
    user_id = cache.get(f"pwd_reset_{token}")

    if user_id is None:
        raise serializers.ValidationError("Invalid or expired token")

    user = User.objects.get(id=user_id)
    user.set_password(new_password)
    user.save()

    cache.delete(f"pwd_reset_{token}")


def verify_email_token(token: str) -> None:
    """
    Mark a user's email as verified using a valid verification token.

    Preconditions:
        - token is a non-empty string
        - token exists in Redis and has not expired
    Postconditions:
        - user.is_verified = True
        - token removed from Redis (single-use enforcement)

    Args:
        token: The email verification token from the verification link.

    Raises:
        serializers.ValidationError: If the token is invalid or expired.
    """
    user_id = cache.get(f"verify_{token}")

    if user_id is None:
        raise serializers.ValidationError("Invalid or expired token")

    user = User.objects.get(id=user_id)
    user.is_verified = True
    user.save(update_fields=["is_verified"])

    cache.delete(f"verify_{token}")

from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from common.response import success_response, error_response
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .services import (
    register_user,
    authenticate_user,
    initiate_password_reset,
    confirm_password_reset,
    verify_email_token,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request) -> Response:
    """
    POST /api/users/register/
    Preconditions:
      - request.data contains username, email, phone_number, password
    Postconditions:
      - 201: User created, Celery task dispatched for verification email
      - 400: Validation errors returned
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = register_user(serializer.validated_data)
        return Response(
            success_response(
                "Registration successful. Please verify your email.",
                UserProfileSerializer(user).data,
                201,
            ),
            status=201,
        )
    return Response(
        error_response("Validation failed.", serializer.errors, 400),
        status=400,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request) -> Response:
    """
    POST /api/users/login/
    Preconditions:
      - request.data contains username/email and password
    Postconditions:
      - 200: Returns {"access": str, "refresh": str}
      - 400: Invalid credentials or unverified account
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(
            success_response("Login successful.", serializer.validated_data, 200),
            status=200,
        )
    return Response(
        error_response("Login failed.", serializer.errors, 400),
        status=400,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request) -> Response:
    """
    POST /api/users/logout/
    Preconditions:
      - Valid JWT in Authorization header
      - request.data contains refresh token
    Postconditions:
      - 200: Refresh token blacklisted
      - 400: Invalid or already-blacklisted token
    """
    refresh_token = request.data.get("refresh")
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            success_response("Logged out successfully.", {}, 200),
            status=200,
        )
    except TokenError:
        return Response(
            error_response("Invalid or expired token.", {}, 400),
            status=400,
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def profile(request) -> Response:
    """
    GET    /api/users/profile/ -> 200: user data
    PUT    /api/users/profile/ -> 200: updated user data
    DELETE /api/users/profile/ -> 204: user soft-deleted (is_active=False)
    Preconditions:
      - request.user is authenticated
    Postconditions:
      - All operations scoped to request.user only
    """
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(
            success_response("Profile retrieved.", serializer.data, 200),
            status=200,
        )

    if request.method == "PUT":
        serializer = UserProfileSerializer(request.user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(
                success_response("Profile updated.", serializer.data, 200),
                status=200,
            )
        return Response(
            error_response("Validation failed.", serializer.errors, 400),
            status=400,
        )

    # DELETE
    request.user.is_active = False
    request.user.save(update_fields=["is_active"])
    return Response(status=204)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_request(request) -> Response:
    """
    POST /api/users/reset-password/
    Postconditions:
      - 200 always (no email enumeration)
      - If email exists: Celery task dispatched with reset token
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        initiate_password_reset(serializer.validated_data["email"])
    return Response(
        success_response(
            "If this email is registered, a reset link has been sent.", {}, 200
        ),
        status=200,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request) -> Response:
    """
    POST /api/users/reset-password-confirm/
    Preconditions:
      - token is valid and not expired (TTL: 1 hour)
    Postconditions:
      - 200: Password updated, token invalidated
      - 400: Invalid/expired token or password mismatch
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            error_response("Validation failed.", serializer.errors, 400),
            status=400,
        )
    try:
        confirm_password_reset(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"],
        )
        return Response(
            success_response("Password reset successful.", {}, 200),
            status=200,
        )
    except serializers.ValidationError as e:
        return Response(
            error_response(str(e.detail[0]), {}, 400),
            status=400,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def verify_email(request) -> Response:
    """
    GET /api/users/verify-email/?token=<token>
    Preconditions:
      - token query param present and valid
    Postconditions:
      - 200: user.is_verified=True, token invalidated
      - 400: Invalid or expired token
    """
    token = request.query_params.get("token")
    if not token:
        return Response(
            error_response("Token is required.", {}, 400),
            status=400,
        )
    try:
        verify_email_token(token)
        return Response(
            success_response("Email verified successfully.", {}, 200),
            status=200,
        )
    except serializers.ValidationError as e:
        return Response(
            error_response(str(e.detail[0]), {}, 400),
            status=400,
        )

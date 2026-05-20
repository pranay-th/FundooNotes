import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

LOGIN_URL = "/api/users/login/"
VERIFY_OTP_URL = "/api/users/login/verify-otp/"
LOGOUT_URL = "/api/users/logout/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def verified_user(db):
    """Create a verified, active user for login tests."""
    user = User.objects.create_user(
        username="loginuser",
        email="login@example.com",
        phone_number="5550001111",
        password="SecurePass123!",
    )
    user.is_verified = True
    user.is_active = True
    user.save()
    return user


def _do_full_login(client, email, password, user_id):
    """
    Helper: complete the 2-step login and return the token payload.
    Mocks the Celery OTP task and reads the OTP directly from cache.
    """
    with patch("users.services.send_login_otp_email.delay"):
        login_response = client.post(
            LOGIN_URL, {"username": email, "password": password}, format="json"
        )
    assert login_response.status_code == 202

    otp = cache.get(f"login_otp_{user_id}")
    assert otp is not None, "OTP was not stored in cache"

    verify_response = client.post(
        VERIFY_OTP_URL, {"username": email, "otp": otp}, format="json"
    )
    assert verify_response.status_code == 200
    return verify_response.data["payload"]


# ---------------------------------------------------------------------------
# Step 1 — POST /api/users/login/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_login_sends_otp(client, verified_user):
    """Valid credentials → 202 and OTP stored in cache."""
    with patch("users.services.send_login_otp_email.delay") as mock_task:
        response = client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": "SecurePass123!"},
            format="json",
        )
    assert response.status_code == 202
    assert "email" in response.data["payload"]
    mock_task.assert_called_once()
    assert cache.get(f"login_otp_{verified_user.id}") is not None


@pytest.mark.django_db
def test_login_invalid_credentials(client, verified_user):
    response = client.post(
        LOGIN_URL,
        {"username": "login@example.com", "password": "WrongPassword!"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_unverified_user(client, db):
    user = User.objects.create_user(
        username="unverified",
        email="unverified@example.com",
        phone_number="5550002222",
        password="SecurePass123!",
    )
    user.is_verified = False
    user.save()
    response = client.post(
        LOGIN_URL,
        {"username": "unverified@example.com", "password": "SecurePass123!"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_inactive_user(client, db):
    user = User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        phone_number="5550003333",
        password="SecurePass123!",
    )
    user.is_verified = True
    user.is_active = False
    user.save()
    response = client.post(
        LOGIN_URL,
        {"username": "inactive@example.com", "password": "SecurePass123!"},
        format="json",
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Step 2 — POST /api/users/login/verify-otp/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_verify_otp_success(client, verified_user):
    """Correct OTP → 200 with access and refresh tokens."""
    with patch("users.services.send_login_otp_email.delay"):
        client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": "SecurePass123!"},
            format="json",
        )

    otp = cache.get(f"login_otp_{verified_user.id}")
    response = client.post(
        VERIFY_OTP_URL,
        {"username": "login@example.com", "otp": otp},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data["payload"]
    assert "refresh" in response.data["payload"]


@pytest.mark.django_db
def test_verify_otp_wrong_otp(client, verified_user):
    """Wrong OTP → 400."""
    with patch("users.services.send_login_otp_email.delay"):
        client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": "SecurePass123!"},
            format="json",
        )

    response = client.post(
        VERIFY_OTP_URL,
        {"username": "login@example.com", "otp": "000000"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_verify_otp_expired(client, verified_user):
    """No OTP in cache (expired or never requested) → 400."""
    response = client.post(
        VERIFY_OTP_URL,
        {"username": "login@example.com", "otp": "123456"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_verify_otp_single_use(client, verified_user):
    """OTP is invalidated after first successful use."""
    with patch("users.services.send_login_otp_email.delay"):
        client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": "SecurePass123!"},
            format="json",
        )

    otp = cache.get(f"login_otp_{verified_user.id}")

    # First use — should succeed
    r1 = client.post(
        VERIFY_OTP_URL, {"username": "login@example.com", "otp": otp}, format="json"
    )
    assert r1.status_code == 200

    # Second use — OTP should be gone
    r2 = client.post(
        VERIFY_OTP_URL, {"username": "login@example.com", "otp": otp}, format="json"
    )
    assert r2.status_code == 400


# ---------------------------------------------------------------------------
# Logout (uses full 2-step login helper)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_logout_success(client, verified_user):
    tokens = _do_full_login(client, "login@example.com", "SecurePass123!", verified_user.id)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = client.post(LOGOUT_URL, {"refresh": tokens["refresh"]}, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_double_logout_returns_400(client, verified_user):
    tokens = _do_full_login(client, "login@example.com", "SecurePass123!", verified_user.id)

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    first_response = client.post(LOGOUT_URL, {"refresh": tokens["refresh"]}, format="json")
    assert first_response.status_code == 200

    # Get a fresh access token via a second login
    tokens2 = _do_full_login(client, "login@example.com", "SecurePass123!", verified_user.id)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens2['access']}")

    # Try to reuse the already-blacklisted refresh token
    second_response = client.post(LOGOUT_URL, {"refresh": tokens["refresh"]}, format="json")
    assert second_response.status_code == 400

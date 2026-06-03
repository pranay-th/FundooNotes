import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch

User = get_user_model()

RESET_REQUEST_URL = "/api/users/reset-password/"
RESET_CONFIRM_URL = "/api/users/reset-password-confirm/"
VERIFY_EMAIL_URL = "/api/users/verify-email/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def verified_user(db):
    """Create a verified, active user for password reset tests."""
    user = User.objects.create_user(
        username="resetuser",
        email="reset@example.com",
        phone_number="5551112222",
        password="OldSecurePass123!",
    )
    user.is_verified = True
    user.is_active = True
    user.save()
    return user


# ---------------------------------------------------------------------------
# Password Reset Request
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@patch("common.tasks.send_password_reset_email.delay")
def test_reset_request_existing_email_returns_200(mock_email, client, verified_user):
    response = client.post(RESET_REQUEST_URL, {"email": verified_user.email}, format="json")
    assert response.status_code == 200
    mock_email.assert_called_once()


@pytest.mark.django_db
@patch("common.tasks.send_password_reset_email.delay")
def test_reset_request_nonexistent_email_returns_200(mock_email, client, db):
    """Even for non-existent emails, the endpoint returns 200 (no enumeration)."""
    response = client.post(RESET_REQUEST_URL, {"email": "nobody@example.com"}, format="json")
    assert response.status_code == 200
    mock_email.assert_not_called()


# ---------------------------------------------------------------------------
# Password Reset Confirm
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_reset_confirm_valid_token_returns_200(client, verified_user):
    token = "validresettoken123"
    cache.set(f"pwd_reset_{token}", verified_user.id, timeout=3600)

    payload = {
        "token": token,
        "new_password": "NewSecurePass456!",
        "confirm_password": "NewSecurePass456!",
    }
    response = client.post(RESET_CONFIRM_URL, payload, format="json")
    assert response.status_code == 200

    # Verify the token was consumed (single-use)
    assert cache.get(f"pwd_reset_{token}") is None


@pytest.mark.django_db
def test_reset_confirm_invalid_token_returns_400(client, db):
    payload = {
        "token": "nonexistenttoken",
        "new_password": "NewSecurePass456!",
        "confirm_password": "NewSecurePass456!",
    }
    response = client.post(RESET_CONFIRM_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_reset_confirm_expired_token_returns_400(client, verified_user):
    """Simulate an expired token by not setting it in cache."""
    payload = {
        "token": "expiredtoken999",
        "new_password": "NewSecurePass456!",
        "confirm_password": "NewSecurePass456!",
    }
    response = client.post(RESET_CONFIRM_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_reset_confirm_password_mismatch_returns_400(client, verified_user):
    token = "mismatchtoken123"
    cache.set(f"pwd_reset_{token}", verified_user.id, timeout=3600)

    payload = {
        "token": token,
        "new_password": "NewSecurePass456!",
        "confirm_password": "DifferentPass789!",
    }
    response = client.post(RESET_CONFIRM_URL, payload, format="json")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_verify_email_success_returns_200(client, db):
    user = User.objects.create_user(
        username="verifyuser",
        email="verify@example.com",
        phone_number="5553334444",
        password="SecurePass123!",
    )
    user.is_verified = False
    user.save()

    token = "validverifytoken123"
    cache.set(f"verify_{token}", user.id, timeout=3600)

    response = client.get(VERIFY_EMAIL_URL, {"token": token})
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.is_verified is True

    # Token should be consumed
    assert cache.get(f"verify_{token}") is None


@pytest.mark.django_db
def test_verify_email_invalid_token_returns_400(client, db):
    response = client.get(VERIFY_EMAIL_URL, {"token": "invalidtoken"})
    assert response.status_code == 400


@pytest.mark.django_db
def test_verify_email_missing_token_returns_400(client, db):
    response = client.get(VERIFY_EMAIL_URL)
    assert response.status_code == 400

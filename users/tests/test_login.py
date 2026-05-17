import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

LOGIN_URL = "/api/users/login/"
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


@pytest.mark.django_db
def test_login_success(client, verified_user):
    payload = {"username": "login@example.com", "password": "SecurePass123!"}
    response = client.post(LOGIN_URL, payload, format="json")
    assert response.status_code == 200
    assert "access" in response.data["payload"]
    assert "refresh" in response.data["payload"]


@pytest.mark.django_db
def test_login_invalid_credentials(client, verified_user):
    payload = {"username": "login@example.com", "password": "WrongPassword!"}
    response = client.post(LOGIN_URL, payload, format="json")
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
    payload = {"username": "unverified@example.com", "password": "SecurePass123!"}
    response = client.post(LOGIN_URL, payload, format="json")
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
    payload = {"username": "inactive@example.com", "password": "SecurePass123!"}
    response = client.post(LOGIN_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_logout_success(client, verified_user):
    # Login first to get tokens
    login_payload = {"username": "login@example.com", "password": "SecurePass123!"}
    login_response = client.post(LOGIN_URL, login_payload, format="json")
    assert login_response.status_code == 200

    access_token = login_response.data["payload"]["access"]
    refresh_token = login_response.data["payload"]["refresh"]

    # Logout with the access token in header and refresh token in body
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = client.post(LOGOUT_URL, {"refresh": refresh_token}, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_double_logout_returns_400(client, verified_user):
    # Login first to get tokens
    login_payload = {"username": "login@example.com", "password": "SecurePass123!"}
    login_response = client.post(LOGIN_URL, login_payload, format="json")
    assert login_response.status_code == 200

    access_token = login_response.data["payload"]["access"]
    refresh_token = login_response.data["payload"]["refresh"]

    # First logout
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    first_response = client.post(LOGOUT_URL, {"refresh": refresh_token}, format="json")
    assert first_response.status_code == 200

    # Second logout with the same (now blacklisted) refresh token
    # Need a new access token since ROTATE_REFRESH_TOKENS is True
    # Re-login to get a fresh access token for the second logout attempt
    client.credentials()
    login_response2 = client.post(LOGIN_URL, login_payload, format="json")
    access_token2 = login_response2.data["payload"]["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token2}")
    second_response = client.post(LOGOUT_URL, {"refresh": refresh_token}, format="json")
    assert second_response.status_code == 400

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

REGISTER_URL = "/api/users/register/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def valid_payload():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "password": "SecurePass123!",
    }


@pytest.mark.django_db
@patch("common.tasks.send_verification_email.delay")
def test_register_success(mock_email, client, valid_payload):
    response = client.post(REGISTER_URL, valid_payload, format="json")
    assert response.status_code == 201
    assert response.data["status"] == 201
    mock_email.assert_called_once()


@pytest.mark.django_db
@patch("common.tasks.send_verification_email.delay")
def test_register_duplicate_email(mock_email, client, valid_payload):
    client.post(REGISTER_URL, valid_payload, format="json")
    payload2 = valid_payload.copy()
    payload2["phone_number"] = "9999999999"
    response = client.post(REGISTER_URL, payload2, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
@patch("common.tasks.send_verification_email.delay")
def test_register_duplicate_phone_number(mock_email, client, valid_payload):
    client.post(REGISTER_URL, valid_payload, format="json")
    payload2 = valid_payload.copy()
    payload2["email"] = "other@example.com"
    response = client.post(REGISTER_URL, payload2, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_weak_password_too_short(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "password": "Ab1!",
    }
    response = client.post(REGISTER_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_weak_password_all_numeric(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "password": "12345678",
    }
    response = client.post(REGISTER_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_missing_email(client):
    payload = {
        "username": "testuser",
        "phone_number": "1234567890",
        "password": "SecurePass123!",
    }
    response = client.post(REGISTER_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_missing_username(client):
    payload = {
        "email": "test@example.com",
        "phone_number": "1234567890",
        "password": "SecurePass123!",
    }
    response = client.post(REGISTER_URL, payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_missing_password(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "1234567890",
    }
    response = client.post(REGISTER_URL, payload, format="json")
    assert response.status_code == 400

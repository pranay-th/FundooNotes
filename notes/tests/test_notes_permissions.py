import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

NOTES_URL = "/api/notes/"


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="owner",
        email="owner@example.com",
        phone_number="1112223333",
        password="SecurePass123!",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="intruder",
        email="intruder@example.com",
        phone_number="4445556666",
        password="SecurePass123!",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_client(other_user):
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def note(auth_client):
    """Create a note owned by the primary user and return its id."""
    response = auth_client.post(
        NOTES_URL,
        {"title": "Owner Note", "content": "Owner content"},
        format="json",
    )
    return response.data["payload"]["id"]


@pytest.mark.django_db
def test_get_note_by_non_owner_returns_403(other_client, note):
    response = other_client.get(f"{NOTES_URL}{note}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_put_note_by_non_owner_returns_403(other_client, note):
    response = other_client.put(
        f"{NOTES_URL}{note}/",
        {"title": "Hacked", "content": "Hacked content"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_patch_note_by_non_owner_returns_403(other_client, note):
    response = other_client.patch(
        f"{NOTES_URL}{note}/",
        {"title": "Hacked"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_note_by_non_owner_returns_403(other_client, note):
    response = other_client.delete(f"{NOTES_URL}{note}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_nonexistent_note_returns_404(auth_client):
    response = auth_client.get(f"{NOTES_URL}99999/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_assign_foreign_label_to_note_returns_error(auth_client, other_user):
    from labels.models import Label

    # Create a label owned by other_user
    foreign_label = Label.objects.create(
        title="Foreign Label",
        created_by=other_user,
    )

    response = auth_client.post(
        NOTES_URL,
        {"title": "Note with foreign label", "content": "content", "label_ids": [foreign_label.id]},
        format="json",
    )
    assert response.status_code == 400

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from notes.models import Note

User = get_user_model()

NOTES_URL = "/api/notes/"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="noteuser",
        email="noteuser@example.com",
        phone_number="1112223333",
        password="SecurePass123!",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def create_note_payload():
    return {
        "title": "Test Note",
        "content": "This is a test note content.",
    }


def _note_pk(user, title: str) -> int:
    """Helper: look up a note's PK from the DB after creation."""
    return Note.objects.get(created_by=user, title=title).pk


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_create_note_success(auth_client, create_note_payload):
    response = auth_client.post(NOTES_URL, create_note_payload, format="json")
    assert response.status_code == 201
    assert response.data["payload"]["title"] == create_note_payload["title"]
    # id must NOT be exposed in the response
    assert "id" not in response.data["payload"]


@pytest.mark.django_db
def test_create_note_missing_title(auth_client):
    response = auth_client.post(NOTES_URL, {"content": "No title here"}, format="json")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_list_notes_returns_only_own_non_trashed(auth_client, user, create_note_payload):
    auth_client.post(NOTES_URL, create_note_payload, format="json")

    other_user = User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        phone_number="9998887777",
        password="SecurePass123!",
    )
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)
    other_client.post(NOTES_URL, {"title": "Other Note", "content": "Other content"}, format="json")

    response = auth_client.get(NOTES_URL)
    assert response.status_code == 200
    notes = response.data["payload"]
    assert len(notes) == 1
    assert notes[0]["title"] == create_note_payload["title"]


@pytest.mark.django_db
def test_list_notes_excludes_trashed(auth_client, user, create_note_payload):
    auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = _note_pk(user, create_note_payload["title"])
    auth_client.delete(f"{NOTES_URL}{note_id}/")

    response = auth_client.get(NOTES_URL)
    assert response.status_code == 200
    assert response.data["payload"] == []


# ---------------------------------------------------------------------------
# Retrieve
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_note_success(auth_client, user, create_note_payload):
    auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = _note_pk(user, create_note_payload["title"])

    response = auth_client.get(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 200
    assert response.data["payload"]["title"] == create_note_payload["title"]
    # id must NOT be in the response payload
    assert "id" not in response.data["payload"]


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_full_update_note(auth_client, user, create_note_payload):
    auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = _note_pk(user, create_note_payload["title"])

    update_payload = {"title": "Updated Title", "content": "Updated content"}
    response = auth_client.put(f"{NOTES_URL}{note_id}/", update_payload, format="json")
    assert response.status_code == 200
    assert response.data["payload"]["title"] == "Updated Title"


@pytest.mark.django_db
def test_partial_update_note(auth_client, user, create_note_payload):
    auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = _note_pk(user, create_note_payload["title"])

    response = auth_client.patch(f"{NOTES_URL}{note_id}/", {"title": "Patched Title"}, format="json")
    assert response.status_code == 200
    assert response.data["payload"]["title"] == "Patched Title"


# ---------------------------------------------------------------------------
# Soft-delete
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_soft_delete_note(auth_client, user, create_note_payload):
    auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = _note_pk(user, create_note_payload["title"])

    response = auth_client.delete(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 204

    # Record still exists in DB but is_trashed=True
    note = Note.objects.get(pk=note_id)
    assert note.is_trashed is True


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_unauthenticated_list_returns_401(client):
    response = client.get(NOTES_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_create_returns_401(client, create_note_payload):
    response = client.post(NOTES_URL, create_note_payload, format="json")
    assert response.status_code == 401

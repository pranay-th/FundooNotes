import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

NOTES_URL = "/api/notes/"


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


@pytest.mark.django_db
def test_create_note_success(auth_client, create_note_payload):
    response = auth_client.post(NOTES_URL, create_note_payload, format="json")
    assert response.status_code == 201
    assert response.data["payload"]["title"] == create_note_payload["title"]


@pytest.mark.django_db
def test_create_note_missing_title(auth_client):
    response = auth_client.post(NOTES_URL, {"content": "No title here"}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_list_notes_returns_only_own_non_trashed(auth_client, user, create_note_payload):
    # Create a note for this user
    auth_client.post(NOTES_URL, create_note_payload, format="json")

    # Create another user with a note
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
    # Create a note then trash it
    create_resp = auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = create_resp.data["payload"]["id"]
    auth_client.delete(f"{NOTES_URL}{note_id}/")

    response = auth_client.get(NOTES_URL)
    assert response.status_code == 200
    notes = response.data["payload"]
    assert len(notes) == 0


@pytest.mark.django_db
def test_get_note_success(auth_client, create_note_payload):
    create_resp = auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = create_resp.data["payload"]["id"]

    response = auth_client.get(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 200
    assert response.data["payload"]["id"] == note_id


@pytest.mark.django_db
def test_full_update_note(auth_client, create_note_payload):
    create_resp = auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = create_resp.data["payload"]["id"]

    update_payload = {"title": "Updated Title", "content": "Updated content"}
    response = auth_client.put(f"{NOTES_URL}{note_id}/", update_payload, format="json")
    assert response.status_code == 200
    assert response.data["payload"]["title"] == "Updated Title"


@pytest.mark.django_db
def test_partial_update_note(auth_client, create_note_payload):
    create_resp = auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = create_resp.data["payload"]["id"]

    response = auth_client.patch(f"{NOTES_URL}{note_id}/", {"title": "Patched Title"}, format="json")
    assert response.status_code == 200
    assert response.data["payload"]["title"] == "Patched Title"


@pytest.mark.django_db
def test_soft_delete_note(auth_client, create_note_payload):
    from notes.models import Note

    create_resp = auth_client.post(NOTES_URL, create_note_payload, format="json")
    note_id = create_resp.data["payload"]["id"]

    response = auth_client.delete(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 204

    # Record still exists but is_trashed=True
    note = Note.objects.get(pk=note_id)
    assert note.is_trashed is True


@pytest.mark.django_db
def test_unauthenticated_list_returns_401(client):
    response = client.get(NOTES_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_create_returns_401(client, create_note_payload):
    response = client.post(NOTES_URL, create_note_payload, format="json")
    assert response.status_code == 401

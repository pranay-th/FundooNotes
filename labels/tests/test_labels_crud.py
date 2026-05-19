import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from labels.models import Label

User = get_user_model()

LABELS_URL = "/api/labels/"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="labeluser",
        email="labeluser@example.com",
        phone_number="1112223333",
        password="SecurePass123!",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        phone_number="9998887777",
        password="SecurePass123!",
    )


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def other_auth_client(other_user):
    c = APIClient()
    c.force_authenticate(user=other_user)
    return c


def _label_pk(user, title: str) -> int:
    """Helper: look up a label's PK from the DB after creation."""
    return Label.objects.get(created_by=user, title=title).pk


# ---------------------------------------------------------------------------
# Create label
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_create_label_success(auth_client):
    response = auth_client.post(LABELS_URL, {"title": "Work"}, format="json")
    assert response.status_code == 201
    # payload is a plain string, not a dict
    assert response.data["payload"] == "Work"
    assert "id" not in response.data


@pytest.mark.django_db
def test_create_label_missing_title(auth_client):
    response = auth_client.post(LABELS_URL, {}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_label_duplicate_title_same_user(auth_client):
    auth_client.post(LABELS_URL, {"title": "Work"}, format="json")
    response = auth_client.post(LABELS_URL, {"title": "Work"}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_label_duplicate_title_different_users(auth_client, other_auth_client):
    """Two different users can have labels with the same title."""
    r1 = auth_client.post(LABELS_URL, {"title": "Work"}, format="json")
    r2 = other_auth_client.post(LABELS_URL, {"title": "Work"}, format="json")
    assert r1.status_code == 201
    assert r2.status_code == 201


# ---------------------------------------------------------------------------
# List labels
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_list_labels_returns_only_own(auth_client, other_auth_client):
    auth_client.post(LABELS_URL, {"title": "My Label"}, format="json")
    other_auth_client.post(LABELS_URL, {"title": "Their Label"}, format="json")

    response = auth_client.get(LABELS_URL)
    assert response.status_code == 200
    # payload is a flat list of title strings
    labels = response.data["payload"]
    assert labels == ["My Label"]


@pytest.mark.django_db
def test_list_labels_empty(auth_client):
    response = auth_client.get(LABELS_URL)
    assert response.status_code == 200
    assert response.data["payload"] == []


# ---------------------------------------------------------------------------
# Retrieve label
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_label_success(auth_client, user):
    auth_client.post(LABELS_URL, {"title": "Personal"}, format="json")
    label_id = _label_pk(user, "Personal")

    response = auth_client.get(f"{LABELS_URL}{label_id}/")
    assert response.status_code == 200
    # payload is a plain string
    assert response.data["payload"] == "Personal"


@pytest.mark.django_db
def test_get_label_not_found(auth_client):
    response = auth_client.get(f"{LABELS_URL}99999/")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update label
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_update_label_put(auth_client, user):
    auth_client.post(LABELS_URL, {"title": "Old Title"}, format="json")
    label_id = _label_pk(user, "Old Title")

    response = auth_client.put(f"{LABELS_URL}{label_id}/", {"title": "New Title"}, format="json")
    assert response.status_code == 200
    assert response.data["payload"] == "New Title"


@pytest.mark.django_db
def test_update_label_patch(auth_client, user):
    auth_client.post(LABELS_URL, {"title": "Original"}, format="json")
    label_id = _label_pk(user, "Original")

    response = auth_client.patch(f"{LABELS_URL}{label_id}/", {"title": "Patched"}, format="json")
    assert response.status_code == 200
    assert response.data["payload"] == "Patched"


@pytest.mark.django_db
def test_update_label_duplicate_title(auth_client, user):
    """Updating to a title that already exists for the same user should return 400."""
    auth_client.post(LABELS_URL, {"title": "Alpha"}, format="json")
    auth_client.post(LABELS_URL, {"title": "Beta"}, format="json")
    label_id = _label_pk(user, "Beta")

    response = auth_client.put(f"{LABELS_URL}{label_id}/", {"title": "Alpha"}, format="json")
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Delete label
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_delete_label_success(auth_client, user):
    auth_client.post(LABELS_URL, {"title": "ToDelete"}, format="json")
    label_id = _label_pk(user, "ToDelete")

    response = auth_client.delete(f"{LABELS_URL}{label_id}/")
    assert response.status_code == 204

    # Hard-deleted — should not exist in DB
    assert not Label.objects.filter(pk=label_id).exists()


# ---------------------------------------------------------------------------
# Authentication required
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_list_labels_unauthenticated(client):
    response = client.get(LABELS_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_label_unauthenticated(client):
    response = client.post(LABELS_URL, {"title": "Work"}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_label_unauthenticated(client, user, db):
    label = Label.objects.create(title="Secret", created_by=user)
    response = client.get(f"{LABELS_URL}{label.pk}/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Ownership enforcement (403)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_label_non_owner_returns_403(auth_client, other_user):
    label = Label.objects.create(title="Theirs", created_by=other_user)

    response = auth_client.get(f"{LABELS_URL}{label.pk}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_label_non_owner_returns_403(auth_client, other_user):
    label = Label.objects.create(title="Theirs", created_by=other_user)

    response = auth_client.put(f"{LABELS_URL}{label.pk}/", {"title": "Mine Now"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_label_non_owner_returns_403(auth_client, other_user):
    label = Label.objects.create(title="Theirs", created_by=other_user)

    response = auth_client.delete(f"{LABELS_URL}{label.pk}/")
    assert response.status_code == 403

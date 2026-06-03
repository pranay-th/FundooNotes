"""
conftest.py — Project-wide pytest fixtures for the fundooNotes test suite.

Provides shared fixtures using factory-boy so individual test modules
don't need to repeat boilerplate user/client setup.

Usage in tests:
    def test_something(api_client, verified_user, auth_client):
        ...
"""

import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ---------------------------------------------------------------------------
# Factory-boy factories
# ---------------------------------------------------------------------------

class UserFactory(factory.django.DjangoModelFactory):
    """
    Creates a User instance with unique, deterministic field values.

    Uses factory.Sequence to guarantee uniqueness across test runs so
    parallel or repeated test invocations never collide on the unique
    email / phone_number / username constraints.
    """

    class Meta:
        model = User
        # Skip post-generation if the password kwarg is handled manually
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    phone_number = factory.Sequence(lambda n: f"{1000000000 + n}")
    is_verified = False
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Hash the password after the object is built/created."""
        raw = extracted if extracted is not None else "SecurePass123!"
        obj.set_password(raw)
        if create:
            obj.save(update_fields=["password"])


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client() -> APIClient:
    """
    An unauthenticated DRF APIClient.

    Use this for endpoints that should be publicly accessible or to test
    that unauthenticated requests are rejected (401).
    """
    return APIClient()


@pytest.fixture
def create_user(db):
    """
    Factory fixture that returns a callable for creating User instances.

    Accepts keyword overrides so tests can customise any field:

        user = create_user(email="custom@example.com", is_verified=True)

    The default password is "SecurePass123!" unless overridden via the
    ``password`` kwarg (it will be hashed automatically by UserFactory).
    """
    def _create_user(**kwargs) -> User:
        return UserFactory.create(**kwargs)

    return _create_user


@pytest.fixture
def verified_user(db) -> User:
    """
    A fully verified, active User ready for login / authenticated requests.

    Password: "SecurePass123!"
    """
    return UserFactory.create(is_verified=True, is_active=True)


@pytest.fixture
def auth_client(verified_user) -> APIClient:
    """
    An APIClient pre-authenticated as ``verified_user`` via a real JWT
    Bearer token in the Authorization header.

    This mirrors production auth (token-based) rather than using
    force_authenticate, so middleware and permission checks run normally.
    """
    refresh = RefreshToken.for_user(verified_user)
    access_token = str(refresh.access_token)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


# ---------------------------------------------------------------------------
# Convenience aliases / additional fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def second_user(db) -> User:
    """
    A second verified user, useful for ownership / isolation tests.

    Password: "SecurePass123!"
    """
    return UserFactory.create(is_verified=True, is_active=True)


@pytest.fixture
def second_auth_client(second_user) -> APIClient:
    """
    An APIClient authenticated as ``second_user``.

    Use alongside ``auth_client`` to test that one user cannot access
    another user's resources.
    """
    refresh = RefreshToken.for_user(second_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client

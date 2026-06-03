"""
Pytest configuration and shared fixtures for the Note Collaboration Service
test suite.

Test isolation strategy
-----------------------
* An in-memory SQLite database (``sqlite+aiosqlite:///:memory:``) is used for
  all tests.  This avoids any dependency on a running PostgreSQL instance and
  keeps tests fast and hermetic.
* All tables are created once per test session via ``Base.metadata.create_all``
  and torn down at session end.
* Each test function receives a fresh ``AsyncSession`` that is rolled back
  after the test, preventing state leakage between tests.
* The FastAPI ``get_db`` dependency is overridden to inject the test session.

Hypothesis profile
------------------
The ``"ci"`` profile runs each property test with ``max_examples=100``.
"""

import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from hypothesis import HealthCheck, settings
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base, Note, NoteCollaborator, User

# ---------------------------------------------------------------------------
# Hypothesis profile
# ---------------------------------------------------------------------------

settings.register_profile(
    "ci",
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci")


# ---------------------------------------------------------------------------
# Test secret — must match what get_current_user uses
# ---------------------------------------------------------------------------

TEST_SECRET = "django-insecure-fundoonotes-dev-secret-key-change-in-production"
TEST_ALGORITHM = "HS256"


# ---------------------------------------------------------------------------
# Async SQLite engine (session-scoped — created once per test session)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def engine():
    """
    Create an in-memory async SQLite engine and build all tables once for the
    entire test session.  The engine is disposed after all tests complete.
    """
    _engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield _engine

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture(scope="session")
def session_factory(engine):
    """Return a session factory bound to the test engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# ---------------------------------------------------------------------------
# Per-test database session with automatic rollback
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a fresh ``AsyncSession`` for each test.

    The session is rolled back after the test completes so that each test
    starts with a clean slate without recreating the schema.
    """
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


# ---------------------------------------------------------------------------
# Override get_db dependency to use the test session
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def async_client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an ``httpx.AsyncClient`` wired to the FastAPI app with the
    ``get_db`` dependency overridden to use the test database session.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def make_token():
    """
    Return a factory function that signs a JWT for a given ``user_id``.

    Usage::

        def test_something(make_token):
            token = make_token(user_id=42)
            headers = {"Authorization": f"Bearer {token}"}
    """

    def _make_token(user_id: int, expired: bool = False) -> str:
        now = datetime.datetime.utcnow()
        if expired:
            exp = now - datetime.timedelta(hours=1)
        else:
            exp = now + datetime.timedelta(hours=1)

        payload = {
            "user_id": user_id,
            "exp": exp,
            "iat": now,
        }
        return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)

    return _make_token


@pytest_asyncio.fixture
async def make_user(db: AsyncSession):
    """
    Return an async factory that inserts a ``User`` row into the test DB.

    Usage::

        async def test_something(make_user):
            user = await make_user(email="alice@example.com")
    """
    _counter = {"n": 0}

    async def _make_user(
        email: str | None = None,
        username: str | None = None,
        is_active: bool = True,
        is_verified: bool = True,
    ) -> User:
        _counter["n"] += 1
        n = _counter["n"]
        user = User(
            email=email or f"user{n}@example.com",
            username=username or f"user{n}",
            is_active=is_active,
            is_verified=is_verified,
        )
        db.add(user)
        await db.flush()  # populate user.id without committing
        return user

    return _make_user


@pytest_asyncio.fixture
async def make_note(db: AsyncSession):
    """
    Return an async factory that inserts a ``Note`` row into the test DB.

    Usage::

        async def test_something(make_note):
            note = await make_note(owner_id=1)
    """
    _counter = {"n": 0}

    async def _make_note(
        owner_id: int,
        title: str | None = None,
        content: str = "",
        color: str = "default",
        is_trashed: bool = False,
        is_archived: bool = False,
    ) -> Note:
        _counter["n"] += 1
        n = _counter["n"]
        note = Note(
            title=title or f"Test Note {n}",
            content=content,
            color=color,
            is_trashed=is_trashed,
            is_archived=is_archived,
            created_by_id=owner_id,
        )
        db.add(note)
        await db.flush()
        return note

    return _make_note


@pytest_asyncio.fixture
async def make_collaborator(db: AsyncSession):
    """
    Return an async factory that inserts a ``NoteCollaborator`` row into the
    test DB.

    Usage::

        async def test_something(make_collaborator):
            collab = await make_collaborator(
                note_id=1, user_id=2, access_level="read"
            )
    """

    async def _make_collaborator(
        note_id: int,
        user_id: int,
        access_level: str = "read",
    ) -> NoteCollaborator:
        record = NoteCollaborator(
            note_id=note_id,
            collaborator_id=user_id,
            access_level=access_level,
        )
        db.add(record)
        await db.flush()
        return record

    return _make_collaborator

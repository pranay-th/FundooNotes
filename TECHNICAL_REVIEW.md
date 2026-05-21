# FundooNotes — Technical Review Guide

A comprehensive reference for your technical review covering architecture, codebase decisions, and likely interview questions.

---

## 1. Project Overview

FundooNotes is a Google Keep-style note-taking backend built as two cooperating services:

| Service | Framework | Port | Responsibility |
|---------|-----------|------|----------------|
| `fundoonotes/` | Django 4.2 + DRF | 8000 | Users, notes, labels, auth, email |
| `collab_service/` | FastAPI 0.111 | 8001 | Note collaboration (invite, access control) |

Both services share a single PostgreSQL database. There is no HTTP communication between them — they coordinate purely through the database and a shared JWT secret.

---

## 2. System Architecture

```
Client
  │
  ├── Bearer JWT ──► Django DRF (port 8000)
  │                     │
  │                     ├── reads/writes: users, notes, labels
  │                     ├── Redis (cache + Celery broker)
  │                     └── Celery worker (email tasks)
  │
  └── Bearer JWT ──► FastAPI (port 8001)
                        │
                        ├── reads: users, notes
                        └── reads/writes: note_collaborators
                              │
                              └── PostgreSQL (shared DB)
```

**Key architectural decisions:**

- **Shared DB, no inter-service HTTP**: FastAPI connects directly to PostgreSQL. No REST calls between services. This avoids network latency and distributed transaction complexity.
- **JWT reuse**: FastAPI decodes the same tokens Django issues. Same `SECRET_KEY`, same `HS256` algorithm. No token exchange or separate auth server needed.
- **Django never modified**: The collab service is purely additive. Django's codebase has zero awareness of `note_collaborators`.
- **Alembic owns only what it creates**: Django migrations manage `users`, `notes`, `labels`. Alembic only manages `note_collaborators`.

---

## 3. Django Backend — `fundoonotes/`

### 3.1 Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| Django | 4.2.13 | Web framework, ORM, admin |
| djangorestframework | 3.15.2 | REST API layer |
| djangorestframework-simplejwt | 5.3.1 | JWT auth + token blacklist |
| drf-spectacular | 0.27.2 | Auto OpenAPI/Swagger docs |
| celery | 5.3.6 | Async task queue |
| redis / django-redis | 5.0.7 / 5.4.0 | Cache backend + Celery broker |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| loguru | 0.7.2 | Structured file logging |
| python-decouple | 3.8 | Environment variable management |
| hypothesis | 6.103.1 | Property-based testing |

### 3.2 Apps

#### `users` app
Handles the full user lifecycle.

**Model** (`users.User` extends `AbstractUser`):
- `email` — unique, used as `USERNAME_FIELD` (login identifier)
- `phone_number` — unique
- `is_verified` — must be `True` before login is allowed
- `db_table = "users"` — explicit table name shared with FastAPI

**Endpoints:**

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/users/register/` | None | Create account, dispatch verification email |
| POST | `/api/users/login/` | None | Returns `{access, refresh}` JWT pair |
| POST | `/api/users/logout/` | JWT | Blacklists the refresh token |
| GET/PUT/DELETE | `/api/users/profile/` | JWT | View, update, or soft-delete account |
| POST | `/api/users/reset-password/` | None | Initiate password reset (no email enumeration) |
| POST | `/api/users/reset-password-confirm/` | None | Complete reset with token |
| GET | `/api/users/verify-email/?token=` | None | Verify email address |

**Auth flow:**
1. Register → Celery dispatches verification email with UUID token stored in Redis (TTL 1h)
2. User clicks link → `verify_email` sets `is_verified=True`, deletes Redis key
3. Login → `authenticate()` checks credentials + `is_verified` + `is_active` → returns JWT pair
4. Logout → refresh token added to SimpleJWT's blacklist table

**Password reset flow:**
1. POST email → UUID token stored in Redis as `pwd_reset_{token}` (TTL 1h), Celery sends email
2. POST token + new password → Redis lookup, `set_password()`, delete Redis key
3. Silent fail on unknown email (prevents user enumeration)

#### `notes` app
Full CRUD for notes with soft-delete and Redis caching.

**Model** (`notes.Note`):
- `title`, `content`, `color` (11 choices), `is_archived`, `is_trashed`
- `created_by` — FK to `users.User` (CASCADE)
- `labels` — M2M to `labels.Label`
- `db_table = "notes"` — explicit table name

**Endpoints:**

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/notes/` | List non-trashed notes (cached per user, TTL 300s) |
| POST | `/api/notes/` | Create note, optionally attach labels |
| GET | `/api/notes/<pk>/` | Retrieve note (cached per note, TTL 300s) |
| PUT/PATCH | `/api/notes/<pk>/` | Full or partial update, invalidates cache |
| DELETE | `/api/notes/<pk>/` | Soft-delete (`is_trashed=True`), invalidates cache |

**Caching strategy:**
- List cache key: `notes_list_{user_id}`
- Detail cache key: `note_detail_{pk}`
- Any write (create/update/delete) invalidates both relevant keys
- Cache backend: Redis via `django-redis`

**Soft delete**: Notes are never hard-deleted by the user. `is_trashed=True` hides them from list/detail views. The FastAPI service also filters out trashed notes from shared note lists.

#### `labels` app
Simple CRUD for user-owned labels.

**Model** (`labels.Label`):
- `title`, `created_by` FK
- `unique_together = ("title", "created_by")` — no duplicate label names per user
- `db_table = "labels"`

**Endpoints:**

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/labels/` | List all labels (returns flat list of title strings) |
| POST | `/api/labels/` | Create label |
| GET/PUT/PATCH/DELETE | `/api/labels/<pk>/` | Retrieve, update, or hard-delete |

Labels are hard-deleted (unlike notes). Deleting a label removes it from all notes via the M2M relationship.

#### `common` app
Cross-cutting concerns shared across all apps.

- **`response.py`**: `success_response()` and `error_response()` — every API response follows `{"message": str, "payload": dict, "status": int}`
- **`exceptions.py`**: Custom DRF exception handler — wraps all 4xx/5xx responses in the standard envelope, logs warnings/errors via Loguru
- **`middleware.py`**:
  - `RequestLoggingMiddleware` — logs every request (method, path, status, duration, user ID) and maintains per-method counters in Redis
  - `ExceptionLoggingMiddleware` — catches unhandled exceptions, returns JSON 500 (never raw Django HTML)
- **`tasks.py`**: Celery tasks for `send_verification_email` and `send_password_reset_email`, both with `max_retries=3` and 60s retry delay

### 3.3 JWT Configuration (SimpleJWT)

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),   # configurable via env
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,       # new refresh token on each use
    "BLACKLIST_AFTER_ROTATION": True,    # old refresh token invalidated
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

The `user_id` claim is embedded in the access token payload by SimpleJWT. The FastAPI service reads this claim to identify the caller.

### 3.4 Celery Setup

- Broker: Redis (`redis://localhost:6379/0`)
- Result backend: Redis (`redis://localhost:6379/0`)
- Cache: Redis DB 1 (`redis://localhost:6379/1`) — separate from broker
- Worker started with `-P solo` on Windows (prefork pool not supported on Windows)
- Tasks use `bind=True` for access to `self.retry()`

---

## 4. FastAPI Collaboration Service — `collab_service/`

### 4.1 Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.111.0 | Web framework |
| uvicorn | 0.29.0 | ASGI server |
| SQLAlchemy (asyncio) | 2.0.30 | Async ORM |
| asyncpg | 0.29.0 | Async PostgreSQL driver |
| alembic | 1.13.1 | Database migrations |
| python-jose | 3.3.0 | JWT decode |
| pydantic | 2.7.1 | Request/response validation |
| python-decouple | 3.8 | Environment config |
| aiosqlite | 0.20.0 | In-memory SQLite for tests |
| httpx | 0.27.0 | Async HTTP client (test client) |
| hypothesis | 6.103.1 | Property-based testing |

### 4.2 Directory Structure

```
collab_service/
├── app/
│   ├── main.py          # App factory, lifespan, router wiring, exception handlers
│   ├── config.py        # Settings singleton (python-decouple)
│   ├── database.py      # Async engine + session factory + get_db dependency
│   ├── auth.py          # JWT decode dependency (get_current_user)
│   ├── models.py        # SQLAlchemy ORM: User, Note (read-only), NoteCollaborator
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── dependencies.py  # require_note_owner, require_collaborator
│   └── routers/
│       ├── health.py        # GET /health
│       ├── collaborators.py # POST/GET/PATCH/DELETE /notes/{id}/collaborators
│       ├── shared_notes.py  # GET /notes/shared
│       └── note_access.py   # GET/PATCH /notes/{id}/content
├── tests/
│   └── conftest.py      # Test fixtures, in-memory SQLite, helper factories
├── alembic/
│   ├── env.py
│   └── versions/0001_create_note_collaborators.py
├── alembic.ini
├── requirements.txt
└── .env
```

### 4.3 API Endpoints

| Method | Path | Auth | Dependency | Description |
|--------|------|------|------------|-------------|
| GET | `/health` | None | — | DB probe, returns 200 or 503 |
| POST | `/notes/{note_id}/collaborators` | JWT | `require_note_owner` | Invite collaborator (upsert) |
| GET | `/notes/{note_id}/collaborators` | JWT | `require_note_owner` | List collaborators |
| PATCH | `/notes/{note_id}/collaborators/{user_id}` | JWT | `require_note_owner` | Update access level |
| DELETE | `/notes/{note_id}/collaborators/{user_id}` | JWT | `require_note_owner` | Remove collaborator |
| GET | `/notes/shared` | JWT | `get_current_user` | Notes shared with me |
| GET | `/notes/{note_id}/content` | JWT | `require_collaborator` | Read shared note |
| PATCH | `/notes/{note_id}/content` | JWT | `require_collaborator` | Update shared note (read_write only) |
| GET | `/docs` | None | — | Swagger UI |
| GET | `/redoc` | None | — | ReDoc UI |

### 4.4 Data Model

**`NoteCollaborator`** (owned by this service):
```sql
CREATE TABLE note_collaborators (
    id              BIGSERIAL PRIMARY KEY,
    note_id         BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    collaborator_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_level    VARCHAR(10) NOT NULL CHECK (access_level IN ('read', 'read_write')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,
    CONSTRAINT uq_note_collaborator UNIQUE (note_id, collaborator_id)
);
```

**`User` and `Note`** are read-only SQLAlchemy mirrors of Django's tables. FastAPI never inserts/updates those rows.

### 4.5 Access Control Logic

Two FastAPI dependencies enforce all access rules:

**`require_note_owner`**: Used on all collaborator-management endpoints.
- Fetches note by ID → 404 if missing
- Checks `note.created_by_id == current_user.user_id` → 403 if not owner
- Returns the `Note` object

**`require_collaborator`**: Used on note-content endpoints.
- Fetches `NoteCollaborator` row for `(note_id, current_user.user_id)` → 403 if not found
- Returns the `NoteCollaborator` object (which carries `access_level`)

Write enforcement in `PATCH /notes/{note_id}/content`:
```python
if collab_record.access_level == "read":
    raise HTTPException(403, "Read-only access.")
```

### 4.6 Duplicate Invite (Upsert) Logic

When a note owner invites a user who is already a collaborator, the service updates the existing record rather than creating a duplicate:

```python
existing = await db.execute(select(NoteCollaborator).where(...))
if existing:
    existing.access_level = body.access_level.value
    await db.commit()
else:
    db.add(NoteCollaborator(...))
    await db.commit()
```

This satisfies the `UNIQUE (note_id, collaborator_id)` constraint and requirement 2.7.

### 4.7 Application Lifecycle (lifespan)

```python
@asynccontextmanager
async def lifespan(app):
    logger.info("Starting up.")
    yield
    await engine.dispose()   # closes all pooled connections cleanly
    logger.info("Shut down.")
```

FastAPI's `lifespan` replaces the deprecated `on_startup`/`on_shutdown` event handlers.

---

## 5. Database Design

### Tables and Ownership

| Table | Owner | Managed by |
|-------|-------|------------|
| `users` | Django | Django migrations |
| `notes` | Django | Django migrations |
| `labels` | Django | Django migrations |
| `notes_labels` (M2M) | Django | Django migrations |
| `note_collaborators` | FastAPI | Alembic |

### Key Constraints

- `users.email` — UNIQUE
- `users.phone_number` — UNIQUE
- `labels.title + created_by` — UNIQUE TOGETHER
- `note_collaborators.(note_id, collaborator_id)` — UNIQUE (prevents duplicate invites)
- `note_collaborators.access_level` — CHECK constraint (`'read'` or `'read_write'`)
- `note_collaborators.note_id` — FK with `ON DELETE CASCADE`
- `note_collaborators.collaborator_id` — FK with `ON DELETE CASCADE`

### Cascade Behavior

Deleting a `Note` → all its `NoteCollaborator` rows are deleted automatically (DB-level cascade).  
Deleting a `User` → all `NoteCollaborator` rows where they are the collaborator are deleted automatically.

---

## 6. Testing Strategy

### Django Tests (pytest-django)

Located in `{app}/tests/`. Run with `pytest` from `fundoonotes/`.

- `users/tests/` — registration, login, password reset flows
- `notes/tests/` — CRUD operations, permission checks
- `labels/tests/` — label CRUD
- `common/tests/` — request counter middleware

Uses `factory-boy` for test data factories and `hypothesis` for property-based tests.

### FastAPI Tests (pytest-asyncio)

Located in `collab_service/tests/`. Run with `pytest` from `collab_service/`.

**Test isolation**: In-memory SQLite (`sqlite+aiosqlite:///:memory:`) — no PostgreSQL needed for tests.

**`conftest.py` fixtures:**

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `engine` | session | Creates SQLite engine + all tables once |
| `db` | function | Fresh `AsyncSession`, rolled back after each test |
| `async_client` | function | `httpx.AsyncClient` with `get_db` overridden |
| `make_token(user_id)` | function | Signs a JWT with the test secret |
| `make_user(db)` | function | Inserts a `User` row, returns instance |
| `make_note(db, owner_id)` | function | Inserts a `Note` row, returns instance |
| `make_collaborator(db, note_id, user_id, access_level)` | function | Inserts a `NoteCollaborator` row |

**Hypothesis profile**: `"ci"` with `max_examples=100` — registered and loaded in `conftest.py`.

---

## 7. Startup Script (`fundoonotes/start.ps1`)

Run from `fundoonotes/`: `.\start.ps1`

**Sequence:**
1. Django migrations (`manage.py migrate`)
2. Alembic migrations (`alembic upgrade head` from `collab_service/`)
3. Celery worker starts in background (logs → `logs/celery.log`)
4. FastAPI starts in background via uvicorn on port 8001 (logs → `logs/collab_service.log`)
5. Django dev server starts in foreground on port 8000
6. On Ctrl+C: both background processes are stopped cleanly

---

## 8. Likely Technical Review Questions

### Architecture & Design

**Q: Why use a separate FastAPI service instead of adding collaboration to Django?**  
The Django backend was treated as a stable, deployed service. Adding collaboration as a separate microservice keeps concerns isolated, allows independent deployment and scaling, and avoids touching tested Django code. The shared-DB approach avoids the complexity of a message bus while still keeping services decoupled at the code level.

**Q: Why share the database instead of having the services communicate via HTTP?**  
HTTP inter-service calls add latency, require service discovery, and introduce distributed transaction problems (what if Django is down when FastAPI needs to read a note?). Since both services are in the same infrastructure and the data model is simple, direct DB access is simpler and more reliable.

**Q: What are the risks of the shared-DB approach?**  
Schema coupling — if Django renames a column in `notes`, FastAPI's SQLAlchemy model breaks silently. Mitigated by treating Django tables as read-only contracts and using explicit column mappings in SQLAlchemy models rather than reflection.

**Q: How does FastAPI know who the user is without calling Django?**  
SimpleJWT embeds `user_id` in the JWT payload. FastAPI decodes the token using the same `SECRET_KEY` and `HS256` algorithm. No Django call needed — the token is self-contained and cryptographically verified.

**Q: What happens if the JWT secret changes in Django?**  
All existing tokens become invalid for both services simultaneously. Both `.env` files must be updated together. This is a deployment concern, not a code concern.

---

### Django-Specific

**Q: Why use `AbstractUser` instead of a custom model from scratch?**  
`AbstractUser` provides password hashing, permissions framework, and admin integration out of the box. We only needed to add `phone_number`, `is_verified`, and change `USERNAME_FIELD` to `email`.

**Q: Why is `email` the `USERNAME_FIELD`?**  
Users log in with email + password, not username + password. Setting `USERNAME_FIELD = "email"` makes Django's `authenticate()` use email as the lookup field.

**Q: How does the token blacklist work?**  
SimpleJWT stores blacklisted refresh tokens in a `token_blacklist_blacklistedtoken` table. On logout, the refresh token is added to this table. On the next refresh attempt, SimpleJWT checks this table and rejects the token. `ROTATE_REFRESH_TOKENS=True` means every use of a refresh token issues a new one and blacklists the old one.

**Q: Why soft-delete notes instead of hard-delete?**  
Soft delete (`is_trashed=True`) allows recovery and avoids cascading issues. The FastAPI service also filters out trashed notes from shared note lists, so the behavior is consistent across both services.

**Q: How does Redis caching work for notes?**  
On `GET /api/notes/`, the service checks `notes_list_{user_id}` in Redis. On a miss, it queries PostgreSQL and stores the result with TTL=300s. Any write operation (create/update/delete) calls `cache.delete()` on the relevant keys to prevent stale reads.

**Q: What is the `common` app for?**  
It holds cross-cutting concerns that don't belong to any single domain app: response formatting, exception handling, middleware, and Celery tasks. This avoids duplication across `users`, `notes`, and `labels`.

**Q: How are emails sent asynchronously?**  
Views call `send_verification_email.delay(email, token)` — the `.delay()` enqueues the task in Redis. The Celery worker picks it up and calls Django's `send_mail()`. If SMTP fails, the task retries up to 3 times with a 60-second delay.

**Q: What does `drf-spectacular` do?**  
It introspects DRF serializers and view decorators (`@extend_schema`) to auto-generate an OpenAPI 3.0 schema. This powers the Swagger UI at `/api/docs/` and ReDoc at `/api/schema/`.

---

### FastAPI-Specific

**Q: What is `asynccontextmanager` / `lifespan` in FastAPI?**  
It's the recommended way to run startup/shutdown logic in FastAPI. Code before `yield` runs on startup; code after `yield` runs on shutdown. Used here to dispose the SQLAlchemy engine's connection pool cleanly.

**Q: Why use async SQLAlchemy instead of the sync version?**  
FastAPI is built on async Python (asyncio/Starlette). Using sync SQLAlchemy would block the event loop during DB queries, eliminating the concurrency benefits of async. `asyncpg` + `create_async_engine` keeps everything non-blocking.

**Q: What is `expire_on_commit=False` in the session factory?**  
By default, SQLAlchemy expires all ORM objects after a commit, requiring a new DB query to access their attributes. In async code, lazy loading is not available, so accessing an expired attribute would raise an error. `expire_on_commit=False` keeps objects usable after commit.

**Q: How does FastAPI dependency injection work?**  
`Depends()` declares a dependency. FastAPI resolves the dependency graph before calling the route handler. `get_db` yields a session; `get_current_user` depends on `oauth2_scheme` (which extracts the Bearer token); `require_note_owner` depends on both `get_current_user` and `get_db`. FastAPI handles the entire chain automatically.

**Q: Why are `User` and `Note` defined as SQLAlchemy models in FastAPI if they're read-only?**  
SQLAlchemy needs mapped classes to construct typed queries and relationships. The models mirror the Django schema but FastAPI never calls `INSERT`/`UPDATE` on them. The `NoteCollaborator.note` and `.collaborator` relationships allow joined queries without raw SQL.

**Q: How does the upsert work for duplicate invites?**  
There's no native upsert — the code does a `SELECT` first, then either `UPDATE` or `INSERT`. The `UNIQUE (note_id, collaborator_id)` constraint acts as a safety net for race conditions; a concurrent insert would raise `IntegrityError`, which the global exception handler converts to HTTP 409.

**Q: How are tests isolated from the real database?**  
`conftest.py` creates an in-memory SQLite engine. The `get_db` FastAPI dependency is overridden via `app.dependency_overrides[get_db] = _override_get_db`. Each test gets a session that is rolled back after the test, so no state leaks between tests.

**Q: Why does the test session use `db.flush()` instead of `db.commit()`?**  
`flush()` sends the SQL to the database and populates auto-generated IDs (like `user.id`) without committing the transaction. Since the test session is rolled back at the end, using `commit()` would make the data permanent and leak between tests.

---

### Security

**Q: How is SQL injection prevented?**  
Django ORM uses parameterized queries by default. Raw SQL in `notes/utils.py` uses `%s` placeholders with a separate parameter list — never string interpolation. FastAPI uses SQLAlchemy's parameterized query builder.

**Q: How is the password stored?**  
Django's `set_password()` hashes passwords using PBKDF2-SHA256 (Django's default). Passwords are never stored in plaintext.

**Q: How does the password reset prevent user enumeration?**  
`reset_password_request` always returns HTTP 200 with the same message regardless of whether the email exists. The `except User.DoesNotExist: pass` block silently ignores unknown emails.

**Q: What prevents a collaborator from managing other collaborators?**  
Routing. Collaborator-management endpoints (`POST/GET/PATCH/DELETE /notes/{id}/collaborators`) use `require_note_owner`, which returns 403 for non-owners. The note-content endpoints (`/notes/{id}/content`) use `require_collaborator`. A collaborator can never reach the management endpoints because they will always fail the ownership check.

---

### Data Integrity

**Q: What happens to `note_collaborators` rows when a note is deleted?**  
The FK `note_id REFERENCES notes(id) ON DELETE CASCADE` causes PostgreSQL to automatically delete all associated `note_collaborators` rows when the note is deleted.

**Q: What happens when a user account is deleted?**  
Django soft-deletes users (`is_active=False`) via the profile DELETE endpoint — the row stays in the DB. If a user were hard-deleted, the FK `collaborator_id REFERENCES users(id) ON DELETE CASCADE` would remove their collaborator records automatically.

**Q: Can a note owner invite themselves?**  
No. The invite endpoint checks `if target_user.id == current_user.user_id` and returns HTTP 400 with "You cannot invite yourself as a collaborator."

---

## 9. Quick Reference — HTTP Status Codes

| Code | When |
|------|------|
| 200 | Successful GET, PUT, PATCH |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no body) |
| 400 | Validation error, self-invite, bad token |
| 401 | Missing/expired/invalid JWT |
| 403 | Not the note owner, not a collaborator, read-only access |
| 404 | Note/user/collaborator not found |
| 409 | Integrity conflict (race condition on duplicate insert) |
| 422 | Pydantic validation error (invalid enum value, etc.) |
| 503 | Database unreachable (health check) |

---

## 10. Environment Variables

Both services use `python-decouple` to load from `.env` files.

| Variable | Used by | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | Both | JWT signing/verification |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Both | PostgreSQL connection |
| `DATABASE_URL` | FastAPI | Async DSN (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Django | Cache + Celery broker |
| `CELERY_BROKER_URL` | Django | Celery broker |
| `JWT_ALGORITHM` | FastAPI | Default `HS256` |
| `JWT_ACCESS_MINUTES` | Django | Access token lifetime (default 60) |
| `JWT_REFRESH_DAYS` | Django | Refresh token lifetime (default 7) |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Django | SMTP credentials |
| `FRONTEND_URL` | Django | Base URL for email links |
| `DEBUG` | Django | Debug mode |

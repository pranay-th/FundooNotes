# FundooNotes — Full Project Documentation

> A Google Keep-style note-taking application built as a full-stack system with a Django REST backend, a FastAPI collaboration microservice, and a React 18 + TypeScript frontend.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Repository Structure](#4-repository-structure)
5. [Backend — Django REST API](#5-backend--django-rest-api)
6. [Collaboration Microservice — FastAPI](#6-collaboration-microservice--fastapi)
7. [Frontend — React SPA](#7-frontend--react-spa)
8. [Authentication Flow](#8-authentication-flow)
9. [API Reference](#9-api-reference)
10. [Data Models](#10-data-models)
11. [Running the Project](#11-running-the-project)
12. [Environment Variables](#12-environment-variables)
13. [Seeding Sample Data](#13-seeding-sample-data)

---

## 1. Project Overview

FundooNotes is a full-stack note-taking application inspired by Google Keep. It supports:

- **User registration and two-factor authentication** (email + OTP)
- **Note management** — create, edit, archive, trash, restore, and permanently delete notes
- **Label management** — create, rename, and delete labels; filter notes by label
- **Note collaboration** — invite other users to view or edit your notes
- **Shared notes view** — see notes others have shared with you
- **Search** — real-time client-side search across note titles and content
- **Theming** — light and dark mode with persistence
- **AI Chatbot** — OpenRouter-powered assistant (chatbot.py)
- **Responsive layout** — works from 320 px to 1920 px

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (React 18 SPA)                    │
│                     http://localhost:5173                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP + Bearer JWT
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
┌─────────────────────┐         ┌─────────────────────────┐
│  Django REST API    │         │  FastAPI Collab Service  │
│  :8000              │         │  :8001                   │
│                     │         │                          │
│  - Auth (register,  │         │  - Shared notes          │
│    login, OTP, JWT) │         │  - Collaborators CRUD    │
│  - Notes CRUD       │         │  - Note content update   │
│  - Labels CRUD      │         │    (for collaborators)   │
│  - User profile     │         │                          │
└──────────┬──────────┘         └──────────┬───────────────┘
           │                               │
           └──────────────┬────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  PostgreSQL Database  │
              │  (shared by both)     │
              └───────────────────────┘
                          │
              ┌───────────┴───────────┐
              │     Redis             │
              │  - OTP storage        │
              │  - Email verify tokens│
              │  - Password reset     │
              │  - Django cache       │
              │  - Celery broker      │
              └───────────────────────┘
```

**Key design decisions:**

- **Separate microservice for collaboration** — keeps the Django monolith clean; the collab service shares the same PostgreSQL DB and JWT secret
- **Celery for async email** — OTP emails, verification emails, and password reset emails are sent asynchronously so the API response is never blocked by SMTP
- **TanStack Query for server state** — eliminates manual loading/error state; cache invalidation is co-located with mutations
- **React Context for UI state** — auth tokens, theme, and sidebar state live in Context + localStorage; no Redux needed
- **Axios interceptor for token refresh** — a single response interceptor handles 401s by silently refreshing the access token and retrying the original request

---

## 3. Technology Stack

### Backend (Django)

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.13 | Runtime |
| Django | 6.0 | Web framework |
| Django REST Framework | 3.x | REST API layer |
| djangorestframework-simplejwt | 5.x | JWT authentication |
| django-cors-headers | 4.9 | CORS for React dev server |
| drf-spectacular | 0.x | OpenAPI / Swagger docs |
| Celery | 5.x | Async task queue |
| django-redis | 5.x | Redis cache backend |
| psycopg2 | 2.x | PostgreSQL adapter |
| python-decouple | 3.x | Environment variable management |
| Loguru | 0.x | Structured logging |
| factory-boy + Faker | — | Test data generation |

### Collaboration Microservice (FastAPI)

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.13 | Runtime |
| FastAPI | 0.x | Async web framework |
| SQLAlchemy (async) | 2.x | ORM for PostgreSQL |
| Alembic | 1.x | Database migrations |
| python-jose | 3.x | JWT verification |
| uvicorn | 0.x | ASGI server |

### Frontend (React)

| Technology | Version | Purpose |
|---|---|---|
| React | 18 | UI library |
| TypeScript | 5.x | Type safety |
| Vite | 6.x | Build tool + dev server |
| Material UI (MUI) | 5.x | Component library + theming |
| React Router | 6.x | Client-side routing |
| TanStack Query | 5.x | Server state management |
| Axios | 1.x | HTTP client |
| React Hook Form | 7.x | Form state management |
| Yup | 1.x | Schema validation |
| react-masonry-css | 1.x | Masonry grid layout |
| MSW | 2.x | API mocking for tests |
| Vitest | 2.x | Test runner |
| fast-check | 3.x | Property-based testing |
| @testing-library/react | 16.x | Component testing |

### Infrastructure

| Technology | Purpose |
|---|---|
| PostgreSQL | Primary relational database |
| Redis | Cache, Celery broker, OTP/token storage |
| Gmail SMTP | Transactional email delivery |

---

## 4. Repository Structure

```
FundooNotes/
├── fundoonotes/                  # Django project root
│   ├── fundoonotes/              # Django settings, URLs, Celery config
│   │   ├── settings.py           # All configuration (env-driven)
│   │   ├── urls.py               # Root URL routing
│   │   └── celery.py             # Celery app factory
│   ├── users/                    # User auth app
│   │   ├── models.py             # Custom User model
│   │   ├── views.py              # Auth endpoints (FBVs)
│   │   ├── serializers.py        # Input/output serializers
│   │   ├── services.py           # Business logic
│   │   └── utils.py              # Token generation helpers
│   ├── notes/                    # Notes app
│   │   ├── models.py             # Note model
│   │   ├── views.py              # Notes CRUD endpoints
│   │   ├── serializers.py        # NoteSerializer
│   │   └── services.py           # Note business logic
│   ├── labels/                   # Labels app
│   │   ├── models.py             # Label model
│   │   ├── views.py              # Labels CRUD endpoints
│   │   ├── serializers.py        # LabelSerializer
│   │   └── services.py           # Label business logic
│   ├── common/                   # Shared utilities
│   │   ├── response.py           # Standardized response helpers
│   │   ├── middleware.py         # Request/exception logging
│   │   ├── exceptions.py         # Custom exception handler
│   │   └── tasks.py              # Celery email tasks
│   ├── start.ps1                 # One-command startup script
│   └── seed_user.py              # Sample data seeder
│
├── collab_service/               # FastAPI microservice
│   ├── app/
│   │   ├── main.py               # FastAPI app factory + CORS
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── auth.py               # JWT verification
│   │   ├── database.py           # Async engine + session
│   │   ├── dependencies.py       # FastAPI dependencies
│   │   └── routers/
│   │       ├── collaborators.py  # Invite/update/remove collaborators
│   │       ├── shared_notes.py   # Get notes shared with current user
│   │       ├── note_access.py    # Update note content (collaborators)
│   │       └── health.py         # Health check
│   └── alembic/                  # DB migrations
│
├── fundoonotes-frontend/         # React SPA
│   ├── src/
│   │   ├── api/                  # Axios instances + API modules
│   │   ├── components/
│   │   │   ├── auth/             # Login, OTP, Register, Reset forms
│   │   │   ├── common/           # ProtectedRoute, SkeletonCard, etc.
│   │   │   ├── layout/           # AppLayout, TopNav, Sidebar
│   │   │   └── notes/            # NoteCard, NoteEditor, NotesGrid, etc.
│   │   ├── context/              # AuthContext, ThemeContext, UIContext
│   │   ├── hooks/                # useNotes, useLabels, useCollab, useAuth
│   │   ├── pages/                # NotesPage, ArchivePage, TrashPage, etc.
│   │   ├── theme/                # MUI theme + note color palette
│   │   ├── types/                # TypeScript interfaces
│   │   └── utils/                # tokenStorage, searchFilter, constants
│   └── tests/
│       ├── mocks/                # MSW handlers + server
│       └── properties/           # fast-check property tests
│
├── seed_data.py                  # HTTP-based seeder (needs running server)
├── chatbot.py                    # OpenRouter AI chatbot (Streamlit)
└── PROJECT.md                    # This file
```

---

## 5. Backend — Django REST API

### Custom User Model (`users/models.py`)

Extends `AbstractBaseUser` with:
- `username` — display name
- `email` — used as the login identifier (`USERNAME_FIELD = 'email'`)
- `phone_number` — unique, required at registration
- `is_verified` — must be `True` before login is allowed
- `is_active` — soft-delete flag

### Authentication Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/users/register/` | Create account, send verification email |
| GET | `/api/users/verify-email/?token=` | Verify email address |
| POST | `/api/users/login/` | Step 1: validate credentials, send OTP |
| POST | `/api/users/login/verify-otp/` | Step 2: verify OTP, return JWT pair |
| POST | `/api/users/logout/` | Blacklist refresh token |
| POST | `/api/users/reset-password/` | Request password reset email |
| POST | `/api/users/reset-password-confirm/` | Confirm new password with token |
| GET/PUT | `/api/users/profile/` | View or update user profile |
| POST | `/api/token/refresh/` | Refresh access token (simplejwt) |

### Notes Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/notes/` | List all non-trashed notes for current user |
| POST | `/api/notes/` | Create a new note |
| GET | `/api/notes/<id>/` | Retrieve a single note (cached 5 min) |
| PATCH | `/api/notes/<id>/` | Partial update (color, title, archive, trash) |
| DELETE | `/api/notes/<id>/` | Soft-delete (sets `is_trashed=True`) |

### Labels Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/labels/` | List all labels for current user |
| POST | `/api/labels/` | Create a new label |
| PATCH | `/api/labels/<id>/` | Rename a label |
| DELETE | `/api/labels/<id>/` | Delete a label |

### Response Format

All responses follow a consistent envelope:

```json
{
  "message": "Human-readable description",
  "payload": { ... },
  "status": 200
}
```

### Async Email (Celery)

Three Celery tasks handle email delivery:

- `send_verification_email(email, token)` — sends account verification link
- `send_login_otp_email(email, otp)` — sends 6-digit OTP for 2FA login
- `send_password_reset_email(email, token)` — sends password reset link

All tasks retry up to 3 times with a 60-second delay on SMTP failure.

### Token Storage (Redis)

| Redis Key | Value | TTL |
|---|---|---|
| `verify_{token}` | user_id | 3600s (1 hour) |
| `pwd_reset_{token}` | user_id | 3600s (1 hour) |
| `login_otp_{user_id}` | 6-digit OTP | 300s (5 minutes) |

### Security

- Passwords hashed with Django's PBKDF2 + SHA256
- JWT access tokens expire in 60 minutes (configurable)
- JWT refresh tokens expire in 7 days (configurable)
- Refresh tokens are blacklisted on logout
- Rate limiting: 100 req/day (anon), 1000 req/day (authenticated)
- CORS restricted to `localhost:5173` in development

---

## 6. Collaboration Microservice — FastAPI

Runs independently on port 8001. Shares the same PostgreSQL database and JWT secret as Django.

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/notes/shared` | Notes shared with the current user |
| GET | `/notes/{id}/collaborators` | List collaborators for a note |
| POST | `/notes/{id}/collaborators` | Invite a collaborator by email |
| PATCH | `/notes/{id}/collaborators/{user_id}` | Update access level |
| DELETE | `/notes/{id}/collaborators/{user_id}` | Remove a collaborator |
| PATCH | `/notes/{id}/content` | Update note content (collaborators only) |

### Access Levels

- `read` — can view the note but not edit
- `read_write` — can view and edit the note content

### Authentication

The service verifies the same JWT tokens issued by Django using the shared `SECRET_KEY`. No separate auth system.

---

## 7. Frontend — React SPA

### Routing

| Path | Component | Auth Required |
|---|---|---|
| `/login` | LoginPage | No |
| `/register` | RegisterPage | No |
| `/verify-email?token=` | VerifyEmailPage | No |
| `/reset-password` | ResetPasswordPage | No |
| `/app/notes` | NotesPage | Yes |
| `/app/archive` | ArchivePage | Yes |
| `/app/trash` | TrashPage | Yes |
| `/app/shared` | SharedNotesPage | Yes |
| `/app/labels/:labelId` | LabelPage | Yes |
| `/app/profile` | ProfilePage | Yes |

### State Management

**Server state** (TanStack Query):
- `['notes']` — all notes, stale after 60s
- `['labels']` — all labels, stale after 60s
- `['shared-notes']` — shared notes, stale after 30s
- `['collaborators', noteId]` — collaborators for a note
- `['profile']` — current user profile

**UI state** (React Context):
- `AuthContext` — access token, refresh token, user profile, `isAuthenticated`
- `ThemeContext` — `'light' | 'dark'` mode, `toggleTheme()`
- `UIContext` — sidebar open/closed, search query, active label ID

**Persistence** (localStorage):
- `fundoo_access_token` — JWT access token
- `fundoo_refresh_token` — JWT refresh token
- `fundoo_user` — serialized user profile
- `fundoo_theme` — last selected color mode

### Key Components

**Layout:**
- `AppLayout` — fixed top nav + fixed sidebar + scrollable main content
- `TopNav` — logo, search bar, theme toggle, user avatar menu
- `Sidebar` — navigation items, label list with inline rename/delete, create label

**Notes:**
- `NotesGrid` — responsive masonry grid (4/3/2/1 columns by breakpoint)
- `NoteCard` — displays title, content preview (max 10 lines), label chips, color background; shows action buttons on hover
- `NoteEditor` — dialog for creating/editing notes with title, content, color picker, label picker
- `NoteColorPicker` — popover with 11 color swatches
- `LabelPicker` — popover with checkbox list of labels
- `CollaboratorPanel` — invite by email, set access level, list/remove collaborators

**Common:**
- `ProtectedRoute` — redirects unauthenticated users to `/login`
- `SkeletonCard` — loading placeholder
- `EmptyState` — empty state illustration + message
- `ErrorState` — error message + retry button
- `ConfirmDialog` — generic confirmation dialog (used for permanent delete)

### JWT Interceptor

A single Axios response interceptor on `djangoClient`:
1. On 401 response, reads refresh token from localStorage
2. POSTs to `/api/token/refresh/`
3. On success: updates access token in localStorage + state, retries original request
4. On failure: clears auth state, redirects to `/login`
5. Concurrent 401s are queued — only one refresh call is made

### Note Colors

11 colors with separate light/dark hex values:

| Name | Light | Dark |
|---|---|---|
| Default | #ffffff | #1e1e1e |
| Red | #f28b82 | #b5443a |
| Orange | #fbbc04 | #b5850a |
| Yellow | #fff475 | #b5a800 |
| Green | #ccff90 | #4a7c2f |
| Teal | #a7ffeb | #2a7a6a |
| Blue | #cbf0f8 | #2a6a7a |
| Purple | #d7aefb | #6a2a9a |
| Pink | #fdcfe8 | #9a2a6a |
| Brown | #e6c9a8 | #7a4a2a |
| Gray | #e8eaed | #4a4a4a |

---

## 8. Authentication Flow

### Registration

```
User fills form → POST /api/users/register/
  → User created (is_verified=False)
  → Celery: send_verification_email(email, token)
  → Token stored in Redis: verify_{token} = user_id (TTL 1h)
  → User clicks link: GET /api/users/verify-email/?token=
  → is_verified=True, token deleted from Redis
```

### Two-Factor Login

```
Step 1: POST /api/users/login/ { username: email, password }
  → Credentials validated
  → OTP generated (6 digits)
  → Stored in Redis: login_otp_{user_id} = otp (TTL 5min)
  → Celery: send_login_otp_email(email, otp)
  → Frontend transitions to OTP screen

Step 2: POST /api/users/login/verify-otp/ { username: email, otp }
  → OTP verified against Redis
  → OTP deleted (single-use)
  → JWT pair returned: { access, refresh }
  → Frontend stores tokens in localStorage
  → Navigate to /app/notes
```

### Token Refresh

```
Any API request → 401 response
  → Interceptor fires
  → POST /api/token/refresh/ { refresh }
  → New access token stored
  → Original request retried with new token
  → If refresh fails → logout + redirect to /login
```

---

## 9. API Reference

Full interactive API documentation is available at:
- Django API: `http://localhost:8000/api/docs/` (Swagger UI)
- Collab Service: `http://localhost:8001/docs` (FastAPI auto-docs)

---

## 10. Data Models

### User

```
id            UUID / int  PK
username      string      unique
email         string      unique, login identifier
phone_number  string      unique
password      string      hashed (PBKDF2)
is_verified   boolean     default False
is_active     boolean     default True
created_at    datetime    auto
```

### Note

```
id          int       PK
created_by  FK(User)
title       string    max 255
content     text
color       enum      default|red|orange|yellow|green|teal|blue|purple|pink|brown|gray
is_archived boolean   default False
is_trashed  boolean   default False
labels      M2M(Label)
created_at  datetime  auto
updated_at  datetime  auto
```

### Label

```
id          int       PK
created_by  FK(User)
title       string    max 100, unique per user
created_at  datetime  auto
updated_at  datetime  auto
```

### NoteCollaborator (collab_service)

```
id            int       PK
note_id       int       FK to notes table
user_id       int       FK to users table
access_level  enum      read|read_write
created_at    datetime  auto
```

---

## 11. Running the Project

### Prerequisites

- Python 3.13
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### One-command startup

```powershell
# From the fundoonotes/ directory:
.\start.ps1
```

This script:
1. Runs Django migrations
2. Runs Alembic migrations (collab service)
3. Starts Celery worker (background)
4. Starts FastAPI collab service (background)
5. Starts React frontend via Vite (background)
6. Starts Django dev server (foreground)
7. On Ctrl+C: stops all background processes

### Service URLs

| Service | URL |
|---|---|
| React Frontend | http://localhost:5173 |
| Django API | http://localhost:8000 |
| Django Swagger | http://localhost:8000/api/docs/ |
| Collab Service | http://localhost:8001 |
| Collab Swagger | http://localhost:8001/docs |

### Manual startup (if needed)

```powershell
# Django
cd fundoonotes
python manage.py migrate
python manage.py runserver

# Celery (separate terminal)
cd fundoonotes
python -m celery -A fundoonotes worker --loglevel=info -P solo

# Collab service (separate terminal)
cd collab_service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (separate terminal)
cd fundoonotes-frontend
npm run dev
```

---

## 12. Environment Variables

### Django (`fundoonotes/.env`)

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | False |
| `ALLOWED_HOSTS` | Comma-separated hosts | localhost,127.0.0.1 |
| `DB_NAME` | PostgreSQL database name | — |
| `DB_USER` | PostgreSQL username | — |
| `DB_PASSWORD` | PostgreSQL password | — |
| `DB_HOST` | PostgreSQL host | localhost |
| `DB_PORT` | PostgreSQL port | 5432 |
| `REDIS_URL` | Redis URL for cache | redis://localhost:6379/1 |
| `CELERY_BROKER_URL` | Redis URL for Celery | redis://localhost:6379/0 |
| `CELERY_RESULT_BACKEND` | Redis URL for results | redis://localhost:6379/0 |
| `EMAIL_HOST` | SMTP host | smtp.gmail.com |
| `EMAIL_PORT` | SMTP port | 587 |
| `EMAIL_HOST_USER` | SMTP username | — |
| `EMAIL_HOST_PASSWORD` | SMTP app password | — |
| `DEFAULT_FROM_EMAIL` | From address | noreply@fundoonotes.com |
| `FRONTEND_URL` | Frontend base URL (for email links) | http://localhost:5173 |
| `JWT_ACCESS_MINUTES` | Access token lifetime | 60 |
| `JWT_REFRESH_DAYS` | Refresh token lifetime | 7 |
| `OPENROUTER_API_KEY` | OpenRouter API key (chatbot) | — |

### Frontend (`fundoonotes-frontend/.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_DJANGO_API_URL` | Django API base URL | http://localhost:8000 |
| `VITE_COLLAB_API_URL` | Collab service base URL | http://localhost:8001 |

---

## 13. Seeding Sample Data

### Via Django ORM (no server needed)

```powershell
cd fundoonotes
python seed_user.py
```

Creates 10 labels and 10 notes for the user `pranayth`, including one archived note. Skips existing records (idempotent).

### Via HTTP API (server must be running)

```powershell
cd fundoonotes
python ..\seed_data.py --token <your_access_token>
```

Get a fresh token:

```powershell
python manage.py shell -c "
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
u = User.objects.get(username='pranayth')
print(str(RefreshToken.for_user(u).access_token))
"
```

---

## AI Chatbot

`chatbot.py` is a Streamlit application that provides an AI assistant powered by OpenRouter. It uses the `OPENROUTER_API_KEY` from the Django `.env` file.

```powershell
streamlit run chatbot.py
```

---

*Documentation generated for FundooNotes — BridgeLabz Fellowship Project, May 2026.*

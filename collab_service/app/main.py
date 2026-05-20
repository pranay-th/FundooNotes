"""
FastAPI application factory for the Note Collaboration Service.

Responsibilities
----------------
* Define the ``lifespan`` context manager that creates the async SQLAlchemy
  engine on startup and disposes it cleanly on shutdown.
* Instantiate the ``FastAPI`` application with title, lifespan, and OpenAPI
  documentation URLs.
* Register all four routers: health, collaborators, shared_notes, note_access.
* Add global exception handlers for ``IntegrityError`` (→ 409) and any
  unhandled exception (→ 500).

Requirements: 9.1, 9.2, 9.3
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.database import engine
from app.routers import collaborators, health, note_access, shared_notes

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage the async SQLAlchemy engine lifecycle.

    On startup  : the engine is already created at module import time in
                  ``app.database``; we just log that the service is ready.
    On shutdown : ``engine.dispose()`` closes all pooled connections cleanly,
                  preventing resource leaks when the process exits.
    """
    logger.info("Note Collaboration Service starting up.")
    yield
    await engine.dispose()
    logger.info("Note Collaboration Service shut down. Engine disposed.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Note Collaboration Service",
    description=(
        "A FastAPI microservice that adds multi-user collaboration to "
        "FundooNotes. Shares the same PostgreSQL database and JWT tokens "
        "as the Django backend."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Translate SQLAlchemy ``IntegrityError`` (e.g. unique-constraint violation
    on a race condition) into HTTP 409 Conflict.
    """
    logger.warning("IntegrityError on %s %s: %s", request.method, request.url, exc)
    return JSONResponse(
        status_code=409,
        content={"detail": "A conflicting record already exists."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for any exception not handled by a more specific handler.
    Returns HTTP 500 and logs the full traceback for debugging.
    """
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url, exc_info=exc
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )


# ---------------------------------------------------------------------------
# Router registration
#
# ORDER MATTERS: FastAPI matches routes in registration order. Static path
# segments (/shared, /content) must be registered before dynamic segments
# (/{note_id}/...) that share the same prefix, otherwise FastAPI will try to
# coerce "shared" or "content" into an integer note_id and return 422.
# ---------------------------------------------------------------------------

# Health check — no prefix, no auth required
app.include_router(health.router)

# Shared notes — GET /notes/shared (static segment, must come before /{note_id})
app.include_router(shared_notes.router)

# Note content access — GET/PATCH /notes/{note_id}/content
# (registered before collaborators so /content is not shadowed by /{note_id}/collaborators)
app.include_router(note_access.router)

# Collaborator management — POST/GET/PATCH/DELETE /notes/{note_id}/collaborators
# (dynamic segment, registered last)
app.include_router(collaborators.router)

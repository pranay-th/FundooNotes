"""
Alembic environment configuration for the Note Collaboration Service.

This env.py uses SQLAlchemy's **async** engine (asyncpg) so that Alembic can
run migrations against the same async DSN used by the FastAPI application.

Only the ``note_collaborators`` table is managed here.  The ``notes`` and
``users`` tables are owned by the Django backend and are treated as read-only
from this service's perspective.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# ---------------------------------------------------------------------------
# Make the collab_service package importable when running `alembic` from the
# collab_service/ directory (i.e. add the parent of `app/` to sys.path).
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings  # noqa: E402
from app.models import Base       # noqa: E402

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object that Alembic uses for autogenerate support.
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migrations (no live DB connection)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.  Calls to
    ``context.execute()`` emit the given string to the script output.
    """
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Only manage the note_collaborators table; ignore Django-owned tables.
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (async engine)
# ---------------------------------------------------------------------------

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using an async engine.

    ``asyncpg`` does not support the synchronous ``connect()`` call that
    Alembic uses internally, so we wrap the migration in
    ``run_sync()`` to bridge the async/sync boundary.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,  # no connection pooling during migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

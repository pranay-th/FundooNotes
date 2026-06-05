#!/usr/bin/env bash
# Release script — runs Alembic migrations before the service starts.
# Railway executes this as the releaseCommand before starting the web process.
set -e
echo "Running Alembic migrations..."
alembic upgrade head
echo "Migrations complete."

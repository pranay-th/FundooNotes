"""
test_settings.py — Django settings overrides for the pytest test suite.

Inherits from the main settings and overrides:
  - DATABASE: SQLite file-based (no PostgreSQL needed)
  - CACHES: local-memory (no Redis needed)
  - INSTALLED_APPS: removes apps that don't exist yet (notes, labels)
"""
import os
from fundoonotes.settings import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Database — use SQLite file for tests
# Use a named file so all connections share the same DB
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",  # noqa: F405
        "TEST": {
            "NAME": BASE_DIR / "test_db.sqlite3",  # noqa: F405
        },
    }
}

# ---------------------------------------------------------------------------
# Cache — use local-memory cache instead of Redis
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ---------------------------------------------------------------------------
# Remove apps that haven't been created yet
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    app for app in INSTALLED_APPS  # noqa: F405
    if app not in {"notes", "labels"}
]

# ---------------------------------------------------------------------------
# Disable URL patterns that reference missing apps
# ---------------------------------------------------------------------------
ROOT_URLCONF = "fundoonotes.test_urls"

# ---------------------------------------------------------------------------
# Skip serialization for all apps (speeds up tests)
# ---------------------------------------------------------------------------
TEST_NON_SERIALIZED_APPS = list(INSTALLED_APPS)  # noqa: F405

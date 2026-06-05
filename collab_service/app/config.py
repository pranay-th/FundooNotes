from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from decouple import config


# asyncpg does not support psycopg2-style query parameters like `sslmode` or
# `channel_binding`.  This helper strips them from the URL and returns both a
# clean DSN and a boolean indicating whether SSL should be enabled.
_ASYNCPG_UNSUPPORTED_PARAMS = {"sslmode", "channel_binding"}


def _clean_asyncpg_url(url: str) -> tuple[str, bool]:
    """
    Remove psycopg2-only query parameters from *url* and return
    ``(clean_url, ssl_required)``.

    ``ssl_required`` is ``True`` when the original URL contained
    ``sslmode=require`` (or ``sslmode=verify-full`` / ``sslmode=verify-ca``).
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    sslmode = params.pop("sslmode", ["disable"])[0].lower()
    # Drop all other params not understood by asyncpg
    for key in _ASYNCPG_UNSUPPORTED_PARAMS:
        params.pop(key, None)

    ssl_required = sslmode in ("require", "verify-full", "verify-ca")

    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_parsed = parsed._replace(query=clean_query)
    return urlunparse(clean_parsed), ssl_required


class Settings:
    """
    Application settings loaded from environment variables / .env file
    via python-decouple.

    All database and JWT values mirror the Django backend's configuration
    so that the Collaboration Service can share the same PostgreSQL instance
    and validate the same JWT tokens without any additional setup.
    """

    # JWT / Auth
    SECRET_KEY: str = config("SECRET_KEY")
    JWT_ALGORITHM: str = config("JWT_ALGORITHM", default="HS256")

    # Individual DB connection parameters — optional when DATABASE_URL is set
    DB_HOST: str = config("DB_HOST", default="localhost")
    DB_PORT: int = config("DB_PORT", default=5432, cast=int)
    DB_NAME: str = config("DB_NAME", default="")
    DB_USER: str = config("DB_USER", default="")
    DB_PASSWORD: str = config("DB_PASSWORD", default="")

    # Async SQLAlchemy DSN — used by the engine and Alembic async runner.
    # Falls back to constructing the URL from individual parts if DATABASE_URL
    # is not explicitly set in the environment.
    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        explicit = config("DATABASE_URL", default="")
        if explicit:
            # Railway / NeonDB provides postgresql:// — rewrite to asyncpg scheme
            url = explicit
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            # Strip params that asyncpg doesn't understand (e.g. sslmode)
            url, _ = _clean_asyncpg_url(url)
            return url
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DB_CONNECT_ARGS(self) -> dict:  # noqa: N802
        """
        Extra keyword arguments forwarded to asyncpg's ``connect()``.

        When the raw DATABASE_URL contains ``sslmode=require`` we translate
        that to ``ssl='require'`` which asyncpg understands.
        """
        explicit = config("DATABASE_URL", default="")
        if explicit:
            _, ssl_required = _clean_asyncpg_url(explicit)
            if ssl_required:
                return {"ssl": "require"}
        return {}


# Singleton instance used throughout the application.
settings = Settings()

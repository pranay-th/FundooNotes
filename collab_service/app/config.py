from decouple import config


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

    # Individual DB connection parameters (kept for reference / Alembic use)
    DB_HOST: str = config("DB_HOST", default="localhost")
    DB_PORT: int = config("DB_PORT", default=5432, cast=int)
    DB_NAME: str = config("DB_NAME")
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")

    # Async SQLAlchemy DSN — used by the engine and Alembic async runner.
    # Falls back to constructing the URL from individual parts if DATABASE_URL
    # is not explicitly set in the environment.
    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        explicit = config("DATABASE_URL", default="")
        if explicit:
            return explicit
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Singleton instance used throughout the application.
settings = Settings()

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# ---------------------------------------------------------------------------
# Async engine
# ---------------------------------------------------------------------------
# The engine is created lazily at module import time.  The lifespan handler in
# main.py is responsible for disposing it on shutdown.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,          # set to True for SQL query logging during development
    future=True,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# expire_on_commit=False keeps ORM objects usable after the session is
# committed (important for async code where lazy-loading is not available).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
async def get_db() -> AsyncSession:  # type: ignore[return]
    """
    Yield an async SQLAlchemy session for the duration of a single request.

    Usage::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session

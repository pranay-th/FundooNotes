from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthOut:
    """
    Lightweight liveness + readiness probe.

    Returns ``{"status": "ok", "database": "reachable"}`` when the database
    is accessible, or raises HTTP 503 with
    ``{"status": "degraded", "database": "unreachable"}`` when it is not.
    """
    try:
        await db.execute(text("SELECT 1"))
        return HealthOut(status="ok", database="reachable")
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", "database": "unreachable"},
        )

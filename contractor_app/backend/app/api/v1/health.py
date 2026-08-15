"""Health check endpoints (outside /api/v1 for k8s style, also under router)."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.deps import DbSession
from app.schemas.common import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=HealthOut)
async def live() -> HealthOut:
    return HealthOut(status="ok")


@router.get("/health/ready", response_model=HealthOut)
async def ready(db: DbSession) -> HealthOut:
    await db.execute(text("SELECT 1"))
    return HealthOut(status="ok")

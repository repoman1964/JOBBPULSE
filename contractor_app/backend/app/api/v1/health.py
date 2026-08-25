"""Health check endpoints (outside /api/v1 for k8s style, also under router)."""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.deps import DbSession
from app.schemas.common import HealthOut

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=HealthOut)
async def live() -> HealthOut:
    return HealthOut(status="ok")


@router.get("/health/ready")
async def ready(db: DbSession):
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("ready check failed")
        return JSONResponse({"status": "error"}, status_code=503)
    return HealthOut(status="ok")

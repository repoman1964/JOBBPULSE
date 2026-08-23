"""Unauthenticated demo project read API for Red Clay."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from app.core.config import get_settings
from app.core.deps import DbSession
from app.core.errors import AppError
from app.core.rate_limit import get_limiter
from app.integrations.storage.s3 import ObjectStorage
from app.services.public_demo import (
    DemoProjectDetail,
    get_demo_project,
    list_demo_projects,
    require_email,
)

router = APIRouter(prefix="/public/demo", tags=["public-demo"])


def _check_rate(request: Request) -> None:
    settings = get_settings()
    ip = request.client.host if request.client else "unknown"
    limiter = get_limiter("public_demo", settings.auth_challenge_rate_per_minute)
    if not limiter.allow(ip):
        raise AppError(
            "rate_limited",
            "Too many requests. Try again in a minute.",
            status_code=429,
        )


@router.get("/projects")
async def list_projects(
    request: Request,
    db: DbSession,
    email: str | None = Query(default=None),
) -> dict[str, list]:
    _check_rate(request)
    normalized = require_email(email)
    items = await list_demo_projects(db, normalized, ObjectStorage())
    return {"items": [item.model_dump(by_alias=True) for item in items]}


@router.get("/projects/{slug}")
async def get_project(
    slug: str,
    request: Request,
    db: DbSession,
    email: str | None = Query(default=None),
) -> DemoProjectDetail:
    _check_rate(request)
    normalized = require_email(email)
    return await get_demo_project(db, slug, normalized, ObjectStorage())

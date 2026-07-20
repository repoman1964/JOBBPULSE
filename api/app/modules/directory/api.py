"""Authenticated directory admin routes (§10.11).

Unified publish lives in publishing.api (Phase 7 orchestrator).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.directory import service
from app.modules.directory.schemas import ListingUpdate, ProfileUpdate

router = APIRouter(tags=["directory"])


@router.get("/directory/profile")
async def get_profile(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.get_or_create_profile(db, ctx.company_id)
    return success(payload)


@router.patch("/directory/profile")
async def patch_profile(
    body: ProfileUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_unset=True)
    payload = await service.update_profile(db, ctx.company_id, ctx.role, data)
    return success(payload)


@router.get("/directory/listings")
async def list_listings(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_listings(db, ctx.company_id, limit=limit, offset=offset)
    return success({"items": items, "limit": limit, "offset": offset})


@router.get("/directory/listings/{listing_id}")
async def get_listing(
    listing_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.get_listing(db, ctx.company_id, listing_id)
    return success(payload)


@router.patch("/directory/listings/{listing_id}")
async def patch_listing(
    listing_id: UUID,
    body: ListingUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_unset=True)
    payload = await service.update_listing(db, ctx.company_id, listing_id, ctx.role, data)
    return success(payload)


@router.post("/directory/listings/{listing_id}/publish")
async def publish_listing(
    listing_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.publish_listing(db, ctx.company_id, listing_id, ctx.role)
    return success(payload)


@router.post("/directory/listings/{listing_id}/unpublish")
async def unpublish_listing(
    listing_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.unpublish_listing(db, ctx.company_id, listing_id, ctx.role)
    return success(payload)


@router.post("/jobs/{job_id}/unpublish-directory")
async def unpublish_job_directory(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Secondary control: remove project from public directory."""
    payload = await service.unpublish_for_job(db, ctx.company_id, job_id, ctx.role)
    return success(payload)

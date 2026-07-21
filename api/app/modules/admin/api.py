"""Admin moderation HTTP routes."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context, get_current_user
from app.core.responses import success
from app.db.models import User
from app.db.session import get_db
from app.modules.admin import service

router = APIRouter(tags=["admin"])


class FlagRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)


class RemoveRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=500)


@router.post("/directory/listings/{listing_id}/flag")
async def flag_listing(
    listing_id: UUID,
    body: FlagRequest | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.flag_listing(
        db,
        listing_id=listing_id,
        user=ctx.user,
        company_id=ctx.company_id,
        role=ctx.role,
        reason=(body.reason if body else None),
    )
    return success(payload)


@router.post("/admin/directory/listings/{listing_id}/remove")
async def remove_listing(
    listing_id: UUID,
    body: RemoveRequest | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.remove_listing(
        db,
        listing_id=listing_id,
        user=user,
        reason=(body.reason if body else None),
    )
    return success(payload)


@router.get("/admin/directory/listings")
async def list_admin_listings(
    status: Optional[str] = Query(default="flagged"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_listings_admin(
        db,
        user=user,
        status=status,
        limit=limit,
        offset=offset,
    )
    return success({"items": items, "limit": limit, "offset": offset, "status": status})

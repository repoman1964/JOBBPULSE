"""Notification HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.notifications import service
from app.modules.notifications.schemas import NotificationOut

router = APIRouter(tags=["notifications"])


@router.get("/notifications")
async def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items, unread_count = await service.list_for_user(
        db,
        user_id=ctx.user_id,
        company_id=ctx.company_id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return success(
        {
            "items": [NotificationOut.model_validate(i).model_dump(mode="json") for i in items],
            "unread_count": unread_count,
            "limit": limit,
            "offset": offset,
        }
    )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.mark_read(
        db,
        user_id=ctx.user_id,
        company_id=ctx.company_id,
        notification_id=notification_id,
    )
    return success(NotificationOut.model_validate(payload).model_dump(mode="json"))


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.mark_all_read(
        db,
        user_id=ctx.user_id,
        company_id=ctx.company_id,
    )
    return success(payload)

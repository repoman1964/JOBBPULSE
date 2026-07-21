"""Audit event HTTP routes."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.audit import service
from app.modules.audit.schemas import AuditEventOut

router = APIRouter(tags=["audit"])


@router.get("/audit-events")
async def list_audit_events(
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[UUID] = Query(default=None),
    action: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_events(
        db,
        company_id=ctx.company_id,
        role=ctx.role,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        limit=limit,
        offset=offset,
    )
    return success(
        {
            "items": [AuditEventOut.model_validate(i).model_dump(mode="json") for i in items],
            "limit": limit,
            "offset": offset,
        }
    )

"""Publishing connections + schedule/status/retry/cancel + unified publish routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.publishing import service
from app.modules.publishing.schemas import (
    ConnectionCallback,
    ConnectionStart,
    JobPublishRequest,
    JobScheduleRequest,
)

router = APIRouter(tags=["publishing"])


@router.get("/publishing/connections")
async def list_connections(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_connections(db, ctx.company_id)
    return success({"items": items})


@router.post("/publishing/connections/start")
async def start_connection(
    body: ConnectionStart,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.start_connection(
        db,
        company_id=ctx.company_id,
        role=ctx.role,
        platform=body.platform,
        display_name=body.display_name,
    )
    return success(payload)


@router.post("/publishing/connections/callback")
async def connection_callback(
    body: ConnectionCallback,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.connection_callback(
        db,
        company_id=ctx.company_id,
        role=ctx.role,
        connection_id=body.connection_id,
        auth_code=body.auth_code,
        platform=body.platform,
    )
    return success(payload)


@router.delete("/publishing/connections/{connection_id}")
async def disconnect_connection(
    connection_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.disconnect_connection(
        db,
        company_id=ctx.company_id,
        connection_id=connection_id,
        role=ctx.role,
    )
    return success(payload)


@router.post("/publishing/connections/{connection_id}/verify")
async def verify_connection(
    connection_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.verify_connection(
        db,
        company_id=ctx.company_id,
        connection_id=connection_id,
        role=ctx.role,
    )
    return success(payload)


@router.post("/jobs/{job_id}/publish")
async def publish_job(
    job_id: UUID,
    body: JobPublishRequest | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Unified Publish — directory + social destinations."""
    req = body or JobPublishRequest()
    payload = await service.publish_job(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        role=ctx.role,
        publish_to_directory=req.publish_to_directory,
        social_connection_ids=req.social_connection_ids,
        scheduled_for=req.scheduled_for,
    )
    return success(payload)


@router.post("/jobs/{job_id}/schedule")
async def schedule_job(
    job_id: UUID,
    body: JobScheduleRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.schedule_job(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        role=ctx.role,
        scheduled_for=body.scheduled_for,
        publish_to_directory=body.publish_to_directory,
        social_connection_ids=body.social_connection_ids,
    )
    return success(payload)


@router.get("/jobs/{job_id}/publications")
async def list_publications(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_publications(db, ctx.company_id, job_id)
    return success({"items": items})


@router.post("/publications/{publication_id}/retry")
async def retry_publication(
    publication_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.retry_publication(
        db,
        company_id=ctx.company_id,
        publication_id=publication_id,
        role=ctx.role,
    )
    return success(payload)


@router.post("/publications/{publication_id}/cancel")
async def cancel_publication(
    publication_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.cancel_publication(
        db,
        company_id=ctx.company_id,
        publication_id=publication_id,
        role=ctx.role,
    )
    return success(payload)

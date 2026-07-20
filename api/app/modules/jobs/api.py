"""Jobs and media HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.exceptions import AppError
from app.core.responses import success
from app.db.session import get_db
from app.modules.jobs import service
from app.modules.jobs.schemas import (
    JobCreate,
    JobDetailOut,
    JobSummaryOut,
    JobUpdate,
    MediaCompleteRequest,
    MediaOut,
    MediaReorderRequest,
    MediaUpdate,
    MediaUploadUrlRequest,
    MediaUploadUrlResponse,
)

router = APIRouter(tags=["jobs"])


def _job_summary(job) -> dict:
    return JobSummaryOut.model_validate(service.serialize_job_summary(job)).model_dump(mode="json")


def _job_detail(job) -> dict:
    return JobDetailOut.model_validate(service.serialize_job_detail(job)).model_dump(mode="json")


def _media_out(media) -> dict:
    return MediaOut.model_validate(service.serialize_media(media)).model_dump(mode="json")


@router.get("/jobs")
async def list_jobs(
    include_archived: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    jobs = await service.list_jobs(
        db,
        ctx.company_id,
        include_archived=include_archived,
        limit=limit,
        offset=offset,
    )
    return success([_job_summary(j) for j in jobs])


@router.post("/jobs", status_code=201)
async def create_job(
    body: JobCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.create_job(
        db,
        company_id=ctx.company_id,
        user_id=ctx.user_id,
        role=ctx.role,
        data=body,
    )
    return success(_job_detail(job))


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.get_job(db, ctx.company_id, job_id)
    return success(_job_detail(job))


@router.patch("/jobs/{job_id}")
async def patch_job(
    job_id: UUID,
    body: JobUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.update_job(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        role=ctx.role,
        data=body,
    )
    return success(_job_detail(job))


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_job(db, company_id=ctx.company_id, job_id=job_id, role=ctx.role)
    return success({"deleted": True})


@router.post("/jobs/{job_id}/archive")
async def archive_job(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.archive_job(
        db, company_id=ctx.company_id, job_id=job_id, role=ctx.role
    )
    return success(_job_detail(job))


@router.post("/jobs/{job_id}/media/upload-url", status_code=201)
async def media_upload_url(
    job_id: UUID,
    body: MediaUploadUrlRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.create_upload_url(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        data=body,
    )
    return success(MediaUploadUrlResponse.model_validate(payload).model_dump(mode="json"))


@router.post("/jobs/{job_id}/media/complete")
async def media_complete(
    job_id: UUID,
    body: MediaCompleteRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.complete_upload(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        role=ctx.role,
        data=body,
    )
    return success(_job_detail(job))


@router.post("/jobs/{job_id}/media/upload", status_code=201)
async def media_direct_upload(
    job_id: UUID,
    file: UploadFile = File(...),
    stage_label: str = Form(default="before"),
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Multipart upload fallback (tests + environments where browser→MinIO CORS fails).
    Prefer signed upload-url flow when possible.
    """
    if stage_label not in {"before", "after"}:
        raise AppError(
            "INVALID_STAGE",
            "Only before and after photos are supported.",
            status_code=400,
        )

    content = await file.read()
    if not content:
        raise AppError("EMPTY_FILE", "Uploaded file is empty.", status_code=400)
    if len(content) > 50 * 1024 * 1024:
        raise AppError("FILE_TOO_LARGE", "Max upload size is 50MB.", status_code=400)

    mime = (file.content_type or "application/octet-stream").lower()
    job = await service.complete_upload_with_bytes(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        filename=file.filename or "photo.jpg",
        mime_type=mime,
        stage_label=stage_label,
        content=content,
    )
    return success(_job_detail(job))


@router.get("/jobs/{job_id}/media")
async def list_job_media(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_media(db, ctx.company_id, job_id)
    return success([_media_out(m) for m in items])


@router.post("/jobs/{job_id}/media/reorder")
async def reorder_media(
    job_id: UUID,
    body: MediaReorderRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.reorder_media(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        role=ctx.role,
        media_ids=body.media_ids,
    )
    return success(_job_detail(job))


@router.patch("/media/{media_id}")
async def patch_media(
    media_id: UUID,
    body: MediaUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    media = await service.update_media(
        db,
        company_id=ctx.company_id,
        media_id=media_id,
        role=ctx.role,
        data=body,
    )
    return success(_media_out(media))


@router.delete("/media/{media_id}")
async def delete_media(
    media_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_media(
        db, company_id=ctx.company_id, media_id=media_id, role=ctx.role
    )
    return success({"deleted": True})


@router.post("/media/{media_id}/set-primary")
async def set_primary_media(
    media_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    media = await service.set_primary_media(
        db, company_id=ctx.company_id, media_id=media_id, role=ctx.role
    )
    return success(_media_out(media))

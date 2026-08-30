"""Job capture and media business logic."""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import storage as storage_svc
from app.core.exceptions import AppError, forbidden, not_found
from app.core.permissions import can_create_jobs
from app.db.models import (
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipRole,
    VoiceSummary,
)
from app.modules.jobs import state as job_state
from app.modules.jobs.schemas import (
    JobCreate,
    JobUpdate,
    MediaCompleteRequest,
    MediaUpdate,
    MediaUploadUrlRequest,
)

ALLOWED_STAGE_LABELS = {
    MediaStageLabel.before,
    MediaStageLabel.progress,
    MediaStageLabel.after,
}


def _ensure_can_capture(role: MembershipRole) -> None:
    if not can_create_jobs(role):
        raise forbidden("You do not have permission to create or update jobs.")


def _parse_stage_label(value: str) -> MediaStageLabel:
    try:
        stage = MediaStageLabel(value)
    except ValueError as exc:
        raise AppError(
            "INVALID_STAGE",
            "Stage must be 'before', 'progress', or 'after'.",
            status_code=400,
        ) from exc
    if stage not in ALLOWED_STAGE_LABELS:
        raise AppError(
            "INVALID_STAGE",
            "Only before, progress, and after photos are supported.",
            status_code=400,
        )
    return stage


async def create_job(
    db: AsyncSession,
    *,
    company_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    company_trade: Optional[str] = None,
    data: JobCreate,
) -> Job:
    """
    Create a Job. `data.title` is required and is a private contractor label
    (never for AI/public — see privacy.fields_for_generation).
    """
    _ensure_can_capture(role)
    # title already trimmed/validated by schema
    job = Job(
        company_id=company_id,
        created_by=user_id,
        title=data.title,
        service_key=data.service_key.strip().lower().replace(" ", "_") if data.service_key else None,
        location_display=data.location_display,
        city=data.city,
        state=data.state,
        postal_code=data.postal_code,
        customer_name_private=data.customer_name_private,
        notes=data.notes,
        assigned_crew_member=data.assigned_crew_member,
        status=JobStatus.draft,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return await get_job(db, company_id, job.id)


async def list_jobs(
    db: AsyncSession,
    company_id: UUID,
    *,
    include_archived: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[Job]:
    stmt = (
        select(Job)
        .where(Job.company_id == company_id)
        .options(
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary).selectinload(VoiceSummary.audio_asset),
            selectinload(Job.directory_listing),
        )
        .order_by(Job.updated_at.desc())
        .limit(min(limit, 100))
        .offset(max(offset, 0))
    )
    stmt = stmt.where(Job.deleted_at.is_(None))
    if not include_archived:
        stmt = stmt.where(Job.status != JobStatus.archived)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_job(db: AsyncSession, company_id: UUID, job_id: UUID) -> Job:
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id, Job.company_id == company_id)
        .options(
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary).selectinload(VoiceSummary.audio_asset),
            selectinload(Job.directory_listing),
        )
    )
    job = result.scalar_one_or_none()
    if job is None or job.deleted_at is not None:
        raise not_found("JOB_NOT_FOUND", "Job not found.")
    return job


async def update_job(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    data: JobUpdate,
) -> Job:
    _ensure_can_capture(role)
    job = await get_job(db, company_id, job_id)
    if job.status == JobStatus.archived:
        raise AppError("JOB_ARCHIVED", "Archived jobs cannot be edited.", status_code=400)

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "service_key" and value is not None:
            value = value.strip().lower().replace(" ", "_")
        if field == "title" and value is not None:
            value = value.strip()
        setattr(job, field, value)

    await db.commit()
    return await get_job(db, company_id, job_id)


async def archive_job(
    db: AsyncSession, *, company_id: UUID, job_id: UUID, role: MembershipRole
) -> Job:
    _ensure_can_capture(role)
    job = await get_job(db, company_id, job_id)
    job.status = JobStatus.archived
    await db.commit()
    return await get_job(db, company_id, job_id)


async def delete_job(
    db: AsyncSession, *, company_id: UUID, job_id: UUID, role: MembershipRole
) -> None:
    """Soft-delete: hide from contractor lists; unpublish directory listing; keep media."""
    from datetime import datetime, timezone

    from app.db.models import DirectoryListingStatus

    _ensure_can_capture(role)
    job = await get_job(db, company_id, job_id)
    now = datetime.now(timezone.utc)
    job.deleted_at = now
    listing = job.directory_listing
    if listing is not None and listing.status == DirectoryListingStatus.published:
        listing.status = DirectoryListingStatus.unpublished
        listing.unpublished_at = now
    await db.commit()


def _ready_media(job: Job) -> list[MediaAsset]:
    return [
        m
        for m in job.media_assets
        if m.processing_status != MediaProcessingStatus.pending_upload
        and m.deleted_at is None
    ]


def serialize_photo_counts(job: Job) -> dict:
    counts = job_state.count_photos(_ready_media(job))
    return {
        "total": counts.total,
        "before": counts.before,
        "progress": counts.progress,
        "after": counts.after,
        "has_before_after_pair": counts.has_before_after_pair,
    }


def serialize_next_action(job: Job) -> dict:
    counts = job_state.count_photos(_ready_media(job))
    return job_state.compute_next_action(job, counts, job.voice_summary).as_dict()


def serialize_timeline(job: Job) -> list[dict]:
    counts = job_state.count_photos(_ready_media(job))
    return job_state.compute_timeline(job, counts, job.voice_summary)


def serialize_media(media: MediaAsset, *, include_url: bool = True) -> dict:
    url = None
    if include_url and media.processing_status != MediaProcessingStatus.pending_upload:
        try:
            url = storage_svc.public_or_signed_url(media.storage_key)
        except Exception:  # noqa: BLE001 — URL is best-effort
            url = None
    return {
        "id": media.id,
        "job_id": media.job_id,
        "storage_key": media.storage_key,
        "url": url,
        "original_filename": media.original_filename,
        "mime_type": media.mime_type,
        "file_size_bytes": media.file_size_bytes,
        "width": media.width,
        "height": media.height,
        "asset_type": media.asset_type.value,
        "stage_label": media.stage_label.value,
        "display_order": media.display_order,
        "is_primary": media.is_primary,
        "processing_status": media.processing_status.value,
        "moderation_status": media.moderation_status,
        "created_at": media.created_at,
        "updated_at": media.updated_at,
    }


def serialize_job_summary(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,  # private contractor label
        "service_key": job.service_key,
        "location_display": job.location_display,
        "city": job.city,
        "state": job.state,
        "status": job.status.value,
        "photo_counts": serialize_photo_counts(job),
        "next_action": serialize_next_action(job),
        "timeline": serialize_timeline(job),
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


def serialize_job_detail(job: Job) -> dict:
    # Contractor UI only shows before/after; hide other stages from media list.
    ready = sorted(
        [
            m
            for m in _ready_media(job)
            if m.stage_label
            in (MediaStageLabel.before, MediaStageLabel.progress, MediaStageLabel.after)
        ],
        key=lambda m: (m.display_order, m.created_at),
    )
    voice_payload = None
    if job.voice_summary is not None:
        from app.modules.jobs.voice import serialize_voice

        voice_payload = serialize_voice(job.voice_summary)
    return {
        "id": job.id,
        "company_id": job.company_id,
        "created_by": job.created_by,
        "title": job.title,  # private contractor label
        "service_key": job.service_key,
        "location_display": job.location_display,
        "city": job.city,
        "state": job.state,
        "postal_code": job.postal_code,
        "customer_name_private": job.customer_name_private,
        "customer_consent_status": job.customer_consent_status,
        "status": job.status.value,
        "notes": job.notes,
        "privacy_mode": job.privacy_mode,
        "photo_counts": serialize_photo_counts(job),
        "next_action": serialize_next_action(job),
        "timeline": serialize_timeline(job),
        "media": [serialize_media(m) for m in ready],
        "voice": voice_payload,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "job_started_at": job.job_started_at,
        "job_completed_at": job.job_completed_at,
    }


async def _sync_job_status(db: AsyncSession, job: Job) -> None:
    counts = job_state.count_photos(_ready_media(job))
    new_status = job_state.recompute_capture_status(job, counts, job.voice_summary)
    if new_status != job.status:
        job.status = new_status
        await db.flush()


async def create_upload_url(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    data: MediaUploadUrlRequest,
) -> dict:
    _ensure_can_capture(role)
    job = await get_job(db, company_id, job_id)
    if job.status == JobStatus.archived:
        raise AppError("JOB_ARCHIVED", "Cannot add media to an archived job.", status_code=400)

    mime = data.mime_type.lower().strip()
    if not storage_svc.is_allowed_image_mime(mime):
        raise AppError(
            "UNSUPPORTED_MEDIA_TYPE",
            "Only JPEG, PNG, WebP, or HEIC images are accepted.",
            status_code=400,
            details={"mime_type": mime},
        )

    media_id = uuid4()
    storage_key = storage_svc.build_storage_key(
        company_id=str(company_id),
        job_id=str(job_id),
        media_id=str(media_id),
        mime_type=mime,
        original_filename=data.filename,
    )

    # Next display order among existing assets
    next_order = 0
    if job.media_assets:
        next_order = max(m.display_order for m in job.media_assets) + 1

    stage = _parse_stage_label(data.stage_label)

    media = MediaAsset(
        id=media_id,
        company_id=company_id,
        job_id=job_id,
        uploaded_by=user_id,
        storage_key=storage_key,
        original_filename=data.filename,
        mime_type=mime,
        file_size_bytes=data.file_size_bytes,
        asset_type=MediaAssetType.image,
        stage_label=stage,
        display_order=next_order,
        is_primary=False,
        processing_status=MediaProcessingStatus.pending_upload,
    )
    db.add(media)
    await db.commit()

    try:
        storage_svc.ensure_bucket()
        raw_url = storage_svc.presign_put_url(storage_key, mime)
        upload_url = storage_svc.rewrite_presigned_for_browser(raw_url)
    except Exception as exc:  # noqa: BLE001
        raise AppError(
            "STORAGE_UNAVAILABLE",
            "Could not create a signed upload URL. Check object storage.",
            status_code=503,
            details={"detail": str(exc)},
        ) from exc

    return {
        "media_id": media_id,
        "storage_key": storage_key,
        "upload_url": upload_url,
        "upload_method": "PUT",
        "headers": {"Content-Type": mime},
        "expires_in": 3600,
        "stage_label": data.stage_label,
    }


async def complete_upload(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    data: MediaCompleteRequest,
    skip_existence_check: bool = False,
) -> Job:
    _ensure_can_capture(role)
    job = await get_job(db, company_id, job_id)
    media = next((m for m in job.media_assets if m.id == data.media_id), None)
    if media is None:
        raise not_found("MEDIA_NOT_FOUND", "Media asset not found on this job.")

    if media.processing_status == MediaProcessingStatus.pending_upload:
        if not skip_existence_check:
            try:
                exists = storage_svc.object_exists(media.storage_key)
            except Exception as exc:  # noqa: BLE001
                raise AppError(
                    "STORAGE_UNAVAILABLE",
                    "Could not verify uploaded object.",
                    status_code=503,
                    details={"detail": str(exc)},
                ) from exc
            if not exists:
                raise AppError(
                    "UPLOAD_NOT_FOUND",
                    "Object not found in storage. Finish the signed upload first.",
                    status_code=400,
                )

        media.processing_status = MediaProcessingStatus.ready
        if data.file_size_bytes is not None:
            media.file_size_bytes = data.file_size_bytes
        if data.width is not None:
            media.width = data.width
        if data.height is not None:
            media.height = data.height

        # First image of a stage becomes primary for that stage if none set.
        same_stage = [
            m
            for m in job.media_assets
            if m.stage_label == media.stage_label
            and m.processing_status != MediaProcessingStatus.pending_upload
            and m.id != media.id
            and m.is_primary
        ]
        if not same_stage:
            media.is_primary = True

        await _sync_job_status(db, job)
        await db.commit()

    return await get_job(db, company_id, job_id)


async def complete_upload_with_bytes(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    filename: str,
    mime_type: str,
    stage_label: str,
    content: bytes,
) -> Job:
    """Server-side upload path (tests / CORS fallback)."""
    upload = await create_upload_url(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        data=MediaUploadUrlRequest(
            filename=filename,
            mime_type=mime_type,
            stage_label=stage_label,
            file_size_bytes=len(content),
        ),
    )
    try:
        storage_svc.ensure_bucket()
        storage_svc.put_bytes(upload["storage_key"], content, mime_type)
    except Exception as exc:  # noqa: BLE001
        raise AppError(
            "STORAGE_UNAVAILABLE",
            "Could not store upload.",
            status_code=503,
            details={"detail": str(exc)},
        ) from exc

    return await complete_upload(
        db,
        company_id=company_id,
        job_id=job_id,
        role=role,
        data=MediaCompleteRequest(
            media_id=upload["media_id"],
            file_size_bytes=len(content),
        ),
        skip_existence_check=True,
    )


async def list_media(db: AsyncSession, company_id: UUID, job_id: UUID) -> list[MediaAsset]:
    job = await get_job(db, company_id, job_id)
    return sorted(_ready_media(job), key=lambda m: (m.display_order, m.created_at))


async def get_media(db: AsyncSession, company_id: UUID, media_id: UUID) -> MediaAsset:
    result = await db.execute(
        select(MediaAsset).where(MediaAsset.id == media_id, MediaAsset.company_id == company_id)
    )
    media = result.scalar_one_or_none()
    if media is None:
        raise not_found("MEDIA_NOT_FOUND", "Media asset not found.")
    return media


async def update_media(
    db: AsyncSession,
    *,
    company_id: UUID,
    media_id: UUID,
    role: MembershipRole,
    data: MediaUpdate,
) -> MediaAsset:
    _ensure_can_capture(role)
    media = await get_media(db, company_id, media_id)
    job = await get_job(db, company_id, media.job_id)

    updates = data.model_dump(exclude_unset=True)
    if "stage_label" in updates and updates["stage_label"] is not None:
        media.stage_label = _parse_stage_label(updates["stage_label"])
    if "display_order" in updates and updates["display_order"] is not None:
        media.display_order = updates["display_order"]
    if "is_primary" in updates and updates["is_primary"] is True:
        # Clear other primaries in the same stage
        for other in job.media_assets:
            if (
                other.id != media.id
                and other.stage_label == media.stage_label
                and other.is_primary
            ):
                other.is_primary = False
        media.is_primary = True
    elif "is_primary" in updates and updates["is_primary"] is False:
        media.is_primary = False

    await _sync_job_status(db, job)
    await db.commit()
    return await get_media(db, company_id, media_id)


async def set_primary_media(
    db: AsyncSession, *, company_id: UUID, media_id: UUID, role: MembershipRole
) -> MediaAsset:
    return await update_media(
        db,
        company_id=company_id,
        media_id=media_id,
        role=role,
        data=MediaUpdate(is_primary=True),
    )


async def delete_media(
    db: AsyncSession, *, company_id: UUID, media_id: UUID, role: MembershipRole
) -> None:
    _ensure_can_capture(role)
    media = await get_media(db, company_id, media_id)
    job_id = media.job_id
    storage_svc.delete_object(media.storage_key)
    await db.delete(media)
    await db.flush()
    job = await get_job(db, company_id, job_id)
    await _sync_job_status(db, job)
    await db.commit()


async def reorder_media(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    media_ids: list[UUID],
) -> Job:
    _ensure_can_capture(role)
    job = await get_job(db, company_id, job_id)
    by_id = {m.id: m for m in job.media_assets}
    for index, mid in enumerate(media_ids):
        if mid not in by_id:
            raise not_found("MEDIA_NOT_FOUND", f"Media {mid} not found on this job.")
        by_id[mid].display_order = index
    await db.commit()
    return await get_job(db, company_id, job_id)

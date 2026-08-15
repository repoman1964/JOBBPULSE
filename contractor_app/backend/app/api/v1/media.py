"""Media upload sessions, list, update, delete."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.deps import CurrentAuth, DbSession
from app.core.errors import AppError
from app.integrations.storage.s3 import ObjectStorage
from app.models.enums import MediaKind, PhotoCategory, PublicJobStatus, UploadStatus
from app.models.job import Job
from app.models.media import MediaAsset
from app.schemas.common import MediaAssetOut, UploadSessionOut
from app.schemas.requests import (
    PhotoUploadSessionRequest,
    UpdateMediaRequest,
    VoiceUploadSessionRequest,
)
from app.services.job_status import compute_active_public_status
from app.services.mappers import counts_from_media, media_to_out

router = APIRouter(tags=["media"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}
ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/mp4",
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
    "audio/x-m4a",
    "audio/mp4",
}


async def _get_job(db: DbSession, job_id: UUID, company_id: UUID) -> Job:
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.company_id == company_id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise AppError("not_found", "Job not found.", status_code=404)
    return job


def _media_url(media: MediaAsset, storage: ObjectStorage) -> str:
    key = media.preview_object_key or media.original_object_key
    if not key:
        return ""
    return storage.presign_get(key)


def _thumb_url(media: MediaAsset, storage: ObjectStorage) -> str:
    key = media.thumbnail_object_key or media.preview_object_key or media.original_object_key
    if not key:
        return ""
    return storage.presign_get(key)


async def _refresh_job_status(db: DbSession, job: Job, company_mins: dict) -> None:
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == job.company_id,
        )
    )
    media = list(result.scalars().all())
    counts = counts_from_media(media)
    job.public_status = compute_active_public_status(
        counts=counts,
        minimums=company_mins,
        current=job.public_status,
    )


@router.post(
    "/jobs/{job_id}/media/upload-sessions",
    response_model=UploadSessionOut,
)
async def create_photo_upload_session(
    job_id: UUID,
    body: PhotoUploadSessionRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> UploadSessionOut:
    job = await _get_job(db, job_id, auth.company_id)
    if job.public_status in {
        PublicJobStatus.processing.value,
        PublicJobStatus.publishing.value,
        PublicJobStatus.published.value,
    }:
        raise AppError("job_locked", "Photos cannot be added to this job now.", status_code=409)

    if body.category not in {c.value for c in PhotoCategory}:
        raise AppError("invalid_category", "Category must be before, progress, or after.")

    if body.mime_type not in ALLOWED_IMAGE_TYPES:
        raise AppError(
            "invalid_mime",
            "That photo format is not supported. Use JPEG, PNG, or WebP.",
            status_code=400,
        )

    # Maximums
    maxs = auth.company.photo_maximums_json or {}
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == auth.company_id,
            MediaAsset.kind == MediaKind.photo.value,
            MediaAsset.photo_category == body.category,
            MediaAsset.is_deleted.is_(False),
        )
    )
    existing = list(result.scalars().all())
    cap = int(maxs.get(body.category, 15))
    if len(existing) >= cap:
        raise AppError(
            "max_photos",
            f"You already have the maximum number of {body.category} photos.",
            status_code=400,
        )

    media_id = uuid4()
    key = f"companies/{auth.company_id}/jobs/{job_id}/photos/{media_id}"
    media = MediaAsset(
        id=media_id,
        company_id=auth.company_id,
        job_id=job.id,
        uploaded_by_contractor_id=auth.contractor_id,
        kind=MediaKind.photo.value,
        photo_category=body.category,
        original_object_key=key,
        mime_type=body.mime_type,
        byte_size=body.byte_size,
        checksum=body.checksum,
        upload_status=UploadStatus.pending.value,
        filename=body.filename,
        version=1,
    )
    db.add(media)
    await db.flush()

    storage = ObjectStorage()
    url, expires_at = storage.presign_put(key, content_type=body.mime_type)
    return UploadSessionOut(mediaId=media.id, uploadUrl=url, expiresAt=expires_at)


@router.post(
    "/jobs/{job_id}/media/{media_id}/complete",
    response_model=MediaAssetOut,
)
async def complete_media_upload(
    job_id: UUID,
    media_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> MediaAssetOut:
    job = await _get_job(db, job_id, auth.company_id)
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == auth.company_id,
        )
    )
    media = result.scalar_one_or_none()
    if media is None:
        raise AppError("not_found", "Media not found.", status_code=404)

    storage = ObjectStorage()
    if media.upload_status == UploadStatus.complete.value:
        return media_to_out(
            media,
            url=_media_url(media, storage),
            thumbnail_url=_thumb_url(media, storage),
        )

    key = media.original_object_key
    if not key or not storage.object_exists(key):
        raise AppError(
            "upload_incomplete",
            "We could not find the uploaded file. Please try again.",
            status_code=400,
        )

    head = storage.head_object(key) or {}
    if "ContentLength" in head:
        media.byte_size = int(head["ContentLength"])
    media.upload_status = UploadStatus.complete.value
    media.preview_object_key = key
    media.thumbnail_object_key = key
    await db.flush()
    await _refresh_job_status(db, job, auth.company.photo_minimums_json or {})
    await db.flush()

    return media_to_out(
        media,
        url=_media_url(media, storage),
        thumbnail_url=_thumb_url(media, storage),
    )


@router.get("/jobs/{job_id}/media", response_model=list[MediaAssetOut])
async def list_media(
    job_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
    category: str | None = Query(default=None),
) -> list[MediaAssetOut]:
    await _get_job(db, job_id, auth.company_id)
    stmt = select(MediaAsset).where(
        MediaAsset.job_id == job_id,
        MediaAsset.company_id == auth.company_id,
        MediaAsset.kind == MediaKind.photo.value,
        MediaAsset.is_deleted.is_(False),
    )
    if category:
        stmt = stmt.where(MediaAsset.photo_category == category)
    stmt = stmt.order_by(MediaAsset.created_at.asc())
    result = await db.execute(stmt)
    storage = ObjectStorage()
    return [
        media_to_out(
            m,
            url=_media_url(m, storage),
            thumbnail_url=_thumb_url(m, storage),
        )
        for m in result.scalars().all()
    ]


@router.patch("/jobs/{job_id}/media/{media_id}", response_model=MediaAssetOut)
async def update_media(
    job_id: UUID,
    media_id: UUID,
    body: UpdateMediaRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> MediaAssetOut:
    await _get_job(db, job_id, auth.company_id)
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.job_id == job_id,
            MediaAsset.company_id == auth.company_id,
            MediaAsset.is_deleted.is_(False),
        )
    )
    media = result.scalar_one_or_none()
    if media is None:
        raise AppError("not_found", "Media not found.", status_code=404)

    if body.is_favorite is not None:
        media.is_favorite = body.is_favorite
    if body.photo_category is not None:
        if body.photo_category not in {c.value for c in PhotoCategory}:
            raise AppError("invalid_category", "Invalid photo category.")
        media.photo_category = body.photo_category
    await db.flush()

    job = await _get_job(db, job_id, auth.company_id)
    await _refresh_job_status(db, job, auth.company.photo_minimums_json or {})
    await db.flush()

    storage = ObjectStorage()
    return media_to_out(
        media,
        url=_media_url(media, storage),
        thumbnail_url=_thumb_url(media, storage),
    )


@router.delete("/jobs/{job_id}/media/{media_id}", status_code=204)
async def delete_media(
    job_id: UUID,
    media_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> None:
    job = await _get_job(db, job_id, auth.company_id)
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.job_id == job_id,
            MediaAsset.company_id == auth.company_id,
        )
    )
    media = result.scalar_one_or_none()
    if media is None:
        raise AppError("not_found", "Media not found.", status_code=404)
    media.is_deleted = True
    await db.flush()
    await _refresh_job_status(db, job, auth.company.photo_minimums_json or {})
    await db.flush()


@router.post(
    "/jobs/{job_id}/voice/upload-sessions",
    response_model=UploadSessionOut,
)
async def create_voice_upload_session(
    job_id: UUID,
    body: VoiceUploadSessionRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> UploadSessionOut:
    job = await _get_job(db, job_id, auth.company_id)
    if job.public_status in {
        PublicJobStatus.processing.value,
        PublicJobStatus.publishing.value,
        PublicJobStatus.published.value,
    }:
        raise AppError("job_locked", "Voice cannot be changed for this job now.", status_code=409)

    if body.mime_type not in ALLOWED_AUDIO_TYPES and not body.mime_type.startswith("audio/"):
        raise AppError("invalid_mime", "That audio format is not supported.", status_code=400)

    media_id = uuid4()
    key = f"companies/{auth.company_id}/jobs/{job_id}/voice/{media_id}"
    media = MediaAsset(
        id=media_id,
        company_id=auth.company_id,
        job_id=job.id,
        uploaded_by_contractor_id=auth.contractor_id,
        kind=MediaKind.audio.value,
        photo_category=None,
        original_object_key=key,
        mime_type=body.mime_type,
        byte_size=body.byte_size,
        duration_ms=body.duration_ms,
        upload_status=UploadStatus.pending.value,
        is_active_voice=False,
        version=1,
    )
    db.add(media)
    await db.flush()

    storage = ObjectStorage()
    url, expires_at = storage.presign_put(key, content_type=body.mime_type)
    return UploadSessionOut(mediaId=media.id, uploadUrl=url, expiresAt=expires_at)


@router.post(
    "/jobs/{job_id}/voice/{media_id}/complete",
    response_model=MediaAssetOut,
)
async def complete_voice_upload(
    job_id: UUID,
    media_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> MediaAssetOut:
    job = await _get_job(db, job_id, auth.company_id)
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == auth.company_id,
            MediaAsset.kind == MediaKind.audio.value,
        )
    )
    media = result.scalar_one_or_none()
    if media is None:
        raise AppError("not_found", "Voice recording not found.", status_code=404)

    storage = ObjectStorage()
    if media.upload_status != UploadStatus.complete.value:
        key = media.original_object_key
        if not key or not storage.object_exists(key):
            raise AppError(
                "upload_incomplete",
                "We could not find the uploaded recording. Please try again.",
                status_code=400,
            )
        media.upload_status = UploadStatus.complete.value
        media.preview_object_key = key

    # Retire previous active voice versions
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == auth.company_id,
            MediaAsset.kind == MediaKind.audio.value,
            MediaAsset.is_active_voice.is_(True),
            MediaAsset.id != media.id,
        )
    )
    for old in result.scalars().all():
        old.is_active_voice = False
    media.is_active_voice = True
    await db.flush()

    return media_to_out(
        media,
        url=_media_url(media, storage),
        thumbnail_url=_thumb_url(media, storage),
    )


@router.get("/jobs/{job_id}/voice", response_model=MediaAssetOut | None)
async def get_voice(
    job_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> MediaAssetOut | None:
    await _get_job(db, job_id, auth.company_id)
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job_id,
            MediaAsset.company_id == auth.company_id,
            MediaAsset.kind == MediaKind.audio.value,
            MediaAsset.is_active_voice.is_(True),
            MediaAsset.is_deleted.is_(False),
            MediaAsset.upload_status == UploadStatus.complete.value,
        )
    )
    media = result.scalar_one_or_none()
    if media is None:
        return None
    storage = ObjectStorage()
    return media_to_out(
        media,
        url=_media_url(media, storage),
        thumbnail_url=_thumb_url(media, storage),
    )

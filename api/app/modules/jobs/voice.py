"""Voice summary upload, transcription, and transcript editing."""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import storage as storage_svc
from app.core.exceptions import AppError, not_found
from app.core.permissions import can_create_jobs
from app.db.models import (
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipRole,
    TranscriptionStatus,
    VoiceSummary,
)
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state
from app.modules.jobs.schemas import (
    VoiceCompleteRequest,
    VoiceTranscriptUpdate,
    VoiceUploadUrlRequest,
)
from app.modules.transcription import get_transcription_provider

MAX_AUDIO_BYTES = 25 * 1024 * 1024


def _ensure_can_capture(role: MembershipRole) -> None:
    if not can_create_jobs(role):
        from app.core.exceptions import forbidden

        raise forbidden("You do not have permission to create or update jobs.")


def _normalize_audio_mime(mime_type: str) -> str:
    return mime_type.lower().split(";")[0].strip()


async def _require_after_photos(job: Job) -> None:
    counts = job_state.count_photos(job_service._ready_media(job))
    if counts.after < 1:
        raise AppError(
            "AFTER_PHOTOS_REQUIRED",
            "Add at least one after photo before recording a voice summary.",
            status_code=400,
        )


def _get_voice(job: Job) -> Optional[VoiceSummary]:
    return job.voice_summary


def serialize_voice(voice: VoiceSummary, *, include_audio_url: bool = True) -> dict:
    audio_url = None
    if include_audio_url and voice.audio_asset is not None:
        asset = voice.audio_asset
        if asset.processing_status != MediaProcessingStatus.pending_upload:
            try:
                audio_url = storage_svc.public_or_signed_url(asset.storage_key)
            except Exception:  # noqa: BLE001
                audio_url = None

    edited = (voice.transcript_edited or "").strip() or None
    raw = (voice.transcript_raw or "").strip() or None
    transcript = edited or raw

    return {
        "id": voice.id,
        "job_id": voice.job_id,
        "audio_asset_id": voice.audio_asset_id,
        "audio_url": audio_url,
        "transcript_raw": voice.transcript_raw,
        "transcript_edited": voice.transcript_edited,
        "transcript": transcript,
        "language": voice.language,
        "transcription_status": voice.transcription_status.value,
        "transcription_provider": voice.transcription_provider,
        "transcription_error": voice.transcription_error,
        "created_at": voice.created_at,
        "updated_at": voice.updated_at,
    }


async def get_voice_for_job(
    db: AsyncSession, company_id: UUID, job_id: UUID
) -> VoiceSummary:
    job = await job_service.get_job(db, company_id, job_id)
    voice = _get_voice(job)
    if voice is None:
        raise not_found("VOICE_NOT_FOUND", "No voice summary on this job yet.")
    return voice


async def create_voice_upload_url(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    data: VoiceUploadUrlRequest,
) -> dict:
    _ensure_can_capture(role)
    job = await job_service.get_job(db, company_id, job_id)
    if job.status == JobStatus.archived:
        raise AppError("JOB_ARCHIVED", "Cannot add voice to an archived job.", status_code=400)
    await _require_after_photos(job)

    mime = _normalize_audio_mime(data.mime_type)
    if not storage_svc.is_allowed_audio_mime(mime):
        raise AppError(
            "UNSUPPORTED_MEDIA_TYPE",
            "Unsupported audio type. Use WebM, MP4/M4A, MP3, WAV, or OGG.",
            status_code=400,
            details={"mime_type": mime},
        )
    if data.file_size_bytes is not None and data.file_size_bytes > MAX_AUDIO_BYTES:
        raise AppError(
            "FILE_TOO_LARGE",
            f"Max audio size is {MAX_AUDIO_BYTES // (1024 * 1024)}MB.",
            status_code=400,
        )

    media_id = uuid4()
    storage_key = storage_svc.build_storage_key(
        company_id=str(company_id),
        job_id=str(job_id),
        media_id=str(media_id),
        mime_type=mime,
        original_filename=data.filename,
    )

    next_order = 0
    if job.media_assets:
        next_order = max(m.display_order for m in job.media_assets) + 1

    media = MediaAsset(
        id=media_id,
        company_id=company_id,
        job_id=job_id,
        uploaded_by=user_id,
        storage_key=storage_key,
        original_filename=data.filename,
        mime_type=mime,
        file_size_bytes=data.file_size_bytes,
        duration_seconds=data.duration_seconds,
        asset_type=MediaAssetType.audio,
        stage_label=MediaStageLabel.unclassified,
        display_order=next_order,
        is_primary=False,
        processing_status=MediaProcessingStatus.pending_upload,
    )
    db.add(media)

    voice = _get_voice(job)
    if voice is None:
        voice = VoiceSummary(
            job_id=job_id,
            audio_asset_id=media_id,
            language=data.language or "en",
            transcription_status=TranscriptionStatus.pending,
        )
        db.add(voice)
    else:
        # Re-record: point at new pending asset; clear prior transcripts on complete.
        voice.audio_asset_id = media_id
        voice.language = data.language or voice.language or "en"
        voice.transcription_status = TranscriptionStatus.pending
        voice.transcription_error = None
        voice.transcription_provider = None

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
    }


async def _run_transcription(
    db: AsyncSession,
    *,
    job: Job,
    voice: VoiceSummary,
    media: MediaAsset,
    audio_bytes: Optional[bytes] = None,
) -> VoiceSummary:
    provider = get_transcription_provider()
    voice.transcription_status = TranscriptionStatus.processing
    voice.transcription_provider = provider.name
    voice.transcription_error = None
    await db.flush()

    try:
        if audio_bytes is None:
            audio_bytes = storage_svc.get_object_bytes(media.storage_key)
        text = await provider.transcribe(
            audio_bytes,
            filename=media.original_filename or "audio.webm",
            mime_type=media.mime_type or "audio/webm",
            language=voice.language or "en",
        )
        voice.transcript_raw = (text or "").strip()
        voice.transcript_edited = None  # new audio clears prior edits
        if voice.transcript_raw:
            voice.transcription_status = TranscriptionStatus.completed
        else:
            voice.transcription_status = TranscriptionStatus.failed
            voice.transcription_error = "Provider returned an empty transcript."
    except Exception as exc:  # noqa: BLE001
        voice.transcription_status = TranscriptionStatus.failed
        voice.transcription_error = str(exc)[:2000]
        voice.transcript_raw = None

    await job_service._sync_job_status(db, job)
    await db.commit()
    return await get_voice_for_job(db, job.company_id, job.id)


async def complete_voice_upload(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    data: VoiceCompleteRequest,
    skip_existence_check: bool = False,
    audio_bytes: Optional[bytes] = None,
) -> tuple[VoiceSummary, Job]:
    _ensure_can_capture(role)
    job = await job_service.get_job(db, company_id, job_id)
    await _require_after_photos(job)

    media = next((m for m in job.media_assets if m.id == data.media_id), None)
    if media is None:
        raise not_found("MEDIA_NOT_FOUND", "Media asset not found on this job.")
    if media.asset_type != MediaAssetType.audio:
        raise AppError(
            "INVALID_MEDIA",
            "Voice complete requires an audio media asset.",
            status_code=400,
        )

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
        if data.duration_seconds is not None:
            media.duration_seconds = data.duration_seconds

    voice = _get_voice(job)
    if voice is None:
        voice = VoiceSummary(
            job_id=job_id,
            audio_asset_id=media.id,
            language="en",
            transcription_status=TranscriptionStatus.pending,
        )
        db.add(voice)
        await db.flush()
    else:
        voice.audio_asset_id = media.id

    await db.flush()
    voice = await _run_transcription(
        db, job=job, voice=voice, media=media, audio_bytes=audio_bytes
    )
    job = await job_service.get_job(db, company_id, job_id)
    return voice, job


async def complete_voice_with_bytes(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    filename: str,
    mime_type: str,
    content: bytes,
    language: str = "en",
    duration_seconds: Optional[int] = None,
) -> tuple[VoiceSummary, Job]:
    """Server-side multipart path (tests / CORS fallback)."""
    if not content:
        raise AppError("EMPTY_FILE", "Uploaded file is empty.", status_code=400)
    if len(content) > MAX_AUDIO_BYTES:
        raise AppError(
            "FILE_TOO_LARGE",
            f"Max audio size is {MAX_AUDIO_BYTES // (1024 * 1024)}MB.",
            status_code=400,
        )

    upload = await create_voice_upload_url(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        data=VoiceUploadUrlRequest(
            filename=filename,
            mime_type=mime_type,
            file_size_bytes=len(content),
            duration_seconds=duration_seconds,
            language=language,
        ),
    )
    try:
        storage_svc.ensure_bucket()
        storage_svc.put_bytes(upload["storage_key"], content, _normalize_audio_mime(mime_type))
    except Exception as exc:  # noqa: BLE001
        raise AppError(
            "STORAGE_UNAVAILABLE",
            "Could not store upload.",
            status_code=503,
            details={"detail": str(exc)},
        ) from exc

    return await complete_voice_upload(
        db,
        company_id=company_id,
        job_id=job_id,
        role=role,
        data=VoiceCompleteRequest(
            media_id=upload["media_id"],
            file_size_bytes=len(content),
            duration_seconds=duration_seconds,
        ),
        skip_existence_check=True,
        audio_bytes=content,
    )


async def update_transcript(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    data: VoiceTranscriptUpdate,
) -> tuple[VoiceSummary, Job]:
    _ensure_can_capture(role)
    job = await job_service.get_job(db, company_id, job_id)
    voice = _get_voice(job)
    if voice is None:
        raise not_found("VOICE_NOT_FOUND", "No voice summary on this job yet.")
    if voice.transcription_status != TranscriptionStatus.completed:
        raise AppError(
            "TRANSCRIPT_NOT_READY",
            "Transcript is not ready to edit yet.",
            status_code=400,
        )

    cleaned = (data.transcript_edited or "").strip()
    if not cleaned:
        raise AppError(
            "EMPTY_TRANSCRIPT",
            "Edited transcript cannot be empty.",
            status_code=400,
        )
    voice.transcript_edited = cleaned
    await job_service._sync_job_status(db, job)
    await db.commit()
    voice = await get_voice_for_job(db, company_id, job_id)
    job = await job_service.get_job(db, company_id, job_id)
    return voice, job


async def retranscribe(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
) -> tuple[VoiceSummary, Job]:
    _ensure_can_capture(role)
    job = await job_service.get_job(db, company_id, job_id)
    voice = _get_voice(job)
    if voice is None or voice.audio_asset_id is None:
        raise not_found("VOICE_NOT_FOUND", "No voice audio on this job to retranscribe.")

    media = next((m for m in job.media_assets if m.id == voice.audio_asset_id), None)
    if media is None:
        raise not_found("MEDIA_NOT_FOUND", "Voice audio asset not found.")
    if media.processing_status == MediaProcessingStatus.pending_upload:
        raise AppError(
            "UPLOAD_NOT_FOUND",
            "Audio upload is not complete yet.",
            status_code=400,
        )

    voice = await _run_transcription(db, job=job, voice=voice, media=media)
    job = await job_service.get_job(db, company_id, job_id)
    return voice, job

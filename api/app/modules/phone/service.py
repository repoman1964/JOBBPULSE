"""Contractor-app flows: submit, package, approve-and-publish, social aliases."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, not_found
from app.db.models import (
    ContentVariant,
    ContentVariantStatus,
    Job,
    JobStatus,
    JobSubmission,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipRole,
    PublishingConnection,
    PublishingConnectionStatus,
    VoiceSummary,
)
from app.modules.ai_generation import service as gen_service
from app.modules.ai_generation.schemas import GenerateRequest
from app.modules.content import service as content_service
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state
from app.modules.jobs import voice as voice_svc
from app.modules.jobs.privacy import assert_title_not_in_generation_payload
from app.modules.jobs.schemas import MediaCompleteRequest, MediaUpdate, MediaUploadUrlRequest, VoiceCompleteRequest, VoiceUploadUrlRequest
from app.modules.phone import serialize
from app.modules.phone.status import from_public
from app.modules.publishing import service as publishing_service

SUBMIT_OK = {
    JobStatus.draft,
    JobStatus.before_photos_added,
    JobStatus.work_in_progress,
    JobStatus.ready_for_summary,
    JobStatus.ready_to_generate,
    JobStatus.failed,
    JobStatus.publish_issue,
    JobStatus.revision_requested,
    JobStatus.awaiting_review,
}

APPROVE_OK = {
    JobStatus.awaiting_review,
    JobStatus.revision_requested,
    JobStatus.publish_issue,
    JobStatus.approved,
}


async def _job(db: AsyncSession, company_id: UUID, job_id: UUID) -> Job:
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id, Job.company_id == company_id)
        .options(
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary).selectinload(VoiceSummary.audio_asset),
            selectinload(Job.content_variants),
            selectinload(Job.company),
            selectinload(Job.directory_listing),
            selectinload(Job.structured_details),
        )
    )
    job = result.scalar_one_or_none()
    if job is None or job.deleted_at is not None:
        raise not_found("JOB_NOT_FOUND", "Job not found.")
    return job


def _photo_mins(job: Job) -> dict[str, int]:
    defaults = dict(serialize.DEFAULT_PHOTO_MINS)
    if job.company and job.company.photo_minimums_json:
        defaults.update(job.company.photo_minimums_json)
    return {k: int(defaults.get(k, 0)) for k in ("before", "progress", "after")}


def _assert_submit_ready(job: Job) -> None:
    if job.status not in SUBMIT_OK:
        raise AppError(
            "INVALID_STATUS",
            "This job cannot be submitted in its current state.",
            status_code=400,
            details={"status": job.status.value},
        )
    counts = job_state.count_photos(job_service._ready_media(job))
    mins = _photo_mins(job)
    missing = []
    if counts.before < mins["before"]:
        missing.append(f"before photos ({counts.before}/{mins['before']})")
    if counts.progress < mins["progress"]:
        missing.append(f"progress photos ({counts.progress}/{mins['progress']})")
    if counts.after < mins["after"]:
        missing.append(f"after photos ({counts.after}/{mins['after']})")
    if missing:
        raise AppError(
            "PHOTO_MINIMUMS",
            "Add the required photos before finishing this job: " + ", ".join(missing) + ".",
            status_code=400,
            details={"missing": missing},
        )
    if not job_state.has_usable_transcript(job.voice_summary):
        voice = job.voice_summary
        asset = voice.audio_asset if voice else None
        if asset is None or asset.processing_status == MediaProcessingStatus.pending_upload:
            raise AppError(
                "VOICE_REQUIRED",
                "A voice summary is required before finishing this job.",
                status_code=400,
            )
        raise AppError(
            "VOICE_REQUIRED",
            "A usable voice transcript is required before finishing this job.",
            status_code=400,
        )


async def _find_submission(
    db: AsyncSession, job_id: UUID, kind: str, key: str
) -> Optional[JobSubmission]:
    result = await db.execute(
        select(JobSubmission).where(
            JobSubmission.job_id == job_id,
            JobSubmission.kind == kind,
            JobSubmission.idempotency_key == key,
        )
    )
    return result.scalar_one_or_none()


async def submit_job(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    idempotency_key: str,
) -> Job:
    job = await _job(db, company_id, job_id)
    existing = await _find_submission(db, job_id, "submit", idempotency_key)
    if existing is not None:
        return await _job(db, company_id, job_id)

    _assert_submit_ready(job)

    snapshot = {
        "job_id": str(job.id),
        "company_id": str(job.company_id),
        "service_key": job.service_key,
        "city": job.city,
        "state": job.state,
        "location_display": job.location_display,
        "media_ids": [str(m.id) for m in job_service._ready_media(job) if m.asset_type == MediaAssetType.image],
    }
    assert_title_not_in_generation_payload(snapshot)
    if job.title and job.title in str(snapshot):
        raise AppError(
            "PRIVACY_VIOLATION",
            "Private job name must not appear in generation input.",
            status_code=500,
        )

    job.submitted_at = datetime.now(timezone.utc)
    db.add(
        JobSubmission(
            job_id=job.id,
            company_id=company_id,
            kind="submit",
            idempotency_key=idempotency_key,
            status="processing",
        )
    )
    await db.flush()

    await gen_service.generate(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        body=GenerateRequest(),
    )
    return await _job(db, company_id, job_id)


async def get_package(db: AsyncSession, company_id: UUID, job_id: UUID) -> Optional[dict]:
    job = await _job(db, company_id, job_id)
    return serialize.package_out(job, list(job.content_variants or []))


async def update_featured_media(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    before_id: UUID,
    after_id: UUID,
    role: MembershipRole,
) -> dict:
    job = await _job(db, company_id, job_id)
    ids = {m.id for m in job.media_assets if m.deleted_at is None}
    if before_id not in ids or after_id not in ids:
        raise AppError("MEDIA_NOT_FOUND", "Featured photos must belong to this job.", status_code=400)
    job.featured_before_media_id = before_id
    job.featured_after_media_id = after_id
    await db.commit()
    job = await _job(db, company_id, job_id)
    pkg = serialize.package_out(job, list(job.content_variants or []))
    if pkg is None:
        raise AppError("PACKAGE_NOT_FOUND", "No content package yet. Submit the job first.", status_code=404)
    return pkg


async def request_description_revision(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    instruction: str,
) -> dict:
    await gen_service.regenerate(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        body=GenerateRequest(user_instruction=instruction),
    )
    job = await _job(db, company_id, job_id)
    pkg = serialize.package_out(job, list(job.content_variants or []))
    if pkg is None:
        raise AppError("PACKAGE_NOT_FOUND", "No content package yet.", status_code=404)
    return pkg


async def get_asset(db: AsyncSession, company_id: UUID, asset_id: UUID) -> dict:
    result = await db.execute(
        select(ContentVariant)
        .join(Job, Job.id == ContentVariant.job_id)
        .where(ContentVariant.id == asset_id, Job.company_id == company_id)
        .options(selectinload(ContentVariant.job).selectinload(Job.content_variants))
    )
    variant = result.scalar_one_or_none()
    if variant is None:
        raise not_found("ASSET_NOT_FOUND", "Generated asset not found.")
    dest = serialize._dest_for_variant(variant)
    siblings = [
        v
        for v in (variant.job.content_variants or [])
        if serialize._dest_for_variant(v) == dest
    ]
    return serialize.asset_out(variant, siblings=siblings)


async def revise_asset(
    db: AsyncSession,
    *,
    company_id: UUID,
    asset_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    instruction: str,
) -> dict:
    variant, job = await content_service._load_variant(db, company_id, asset_id)
    await gen_service.regenerate(
        db,
        company_id=company_id,
        job_id=job.id,
        user_id=user_id,
        role=role,
        body=GenerateRequest(user_instruction=instruction),
    )
    # Return the latest variant for the same destination
    job = await _job(db, company_id, job.id)
    dest = serialize._dest_for_variant(variant)
    latest = [
        v
        for v in job.content_variants
        if serialize._dest_for_variant(v) == dest and v.status != ContentVariantStatus.superseded
    ]
    target = latest[-1] if latest else variant
    return await get_asset(db, company_id, target.id)


async def select_asset_version(
    db: AsyncSession,
    *,
    company_id: UUID,
    asset_id: UUID,
    version_id: UUID,
    role: MembershipRole,
) -> dict:
    _ = role
    chosen, job = await content_service._load_variant(db, company_id, version_id)
    dest = serialize._dest_for_variant(chosen)
    for v in job.content_variants or []:
        if serialize._dest_for_variant(v) != dest:
            continue
        if v.id == chosen.id:
            if v.status == ContentVariantStatus.superseded:
                v.status = ContentVariantStatus.awaiting_review
        else:
            v.status = ContentVariantStatus.superseded
    job.status = JobStatus.awaiting_review
    await db.commit()
    return await get_asset(db, company_id, chosen.id)


async def approve_and_publish(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    idempotency_key: str,
) -> Job:
    job = await _job(db, company_id, job_id)
    existing = await _find_submission(db, job_id, "approve_publish", idempotency_key)
    if existing is not None:
        return await _job(db, company_id, job_id)
    if job.status not in APPROVE_OK:
        raise AppError(
            "INVALID_STATUS",
            "Approve is only available when a package is ready for review.",
            status_code=400,
            details={"status": job.status.value},
        )

    db.add(
        JobSubmission(
            job_id=job.id,
            company_id=company_id,
            kind="approve_publish",
            idempotency_key=idempotency_key,
            status="processing",
        )
    )
    job.status = JobStatus.publishing
    await db.flush()

    try:
        await content_service.approve_all(
            db,
            company_id=company_id,
            job_id=job_id,
            user_id=user_id,
            role=role,
        )
        connections = await publishing_service.list_connections(db, company_id)
        active_ids = []
        for c in connections:
            plat = c.get("platform")
            st = c.get("status")
            if plat in {"facebook", "instagram", "google_business"} and st == "active":
                cid = c.get("id")
                active_ids.append(cid if isinstance(cid, UUID) else UUID(str(cid)))
        await publishing_service.publish_job(
            db,
            company_id=company_id,
            job_id=job_id,
            role=role,
            publish_to_directory=True,
            social_connection_ids=active_ids or None,
        )
    except AppError:
        job = await _job(db, company_id, job_id)
        job.status = JobStatus.publish_issue
        await db.commit()
        raise

    job = await _job(db, company_id, job_id)
    if job.directory_listing is None:
        job.status = JobStatus.publish_issue
        await db.commit()
        return await _job(db, company_id, job_id)
    job.status = JobStatus.published
    job.published_at = job.published_at or datetime.now(timezone.utc)
    await db.commit()
    return await _job(db, company_id, job_id)


def social_connections_out(rows: list[dict]) -> list[dict]:
    wanted = ("facebook", "instagram", "google_business")
    by_platform = {}
    for row in rows:
        plat = (row.get("platform") or "").replace("google", "google_business")
        if plat == "gbp":
            plat = "google_business"
        if plat in wanted:
            by_platform[plat] = row
    out = []
    for plat in wanted:
        row = by_platform.get(plat)
        status = "not_connected"
        account = None
        reason = None
        if row:
            raw = row.get("status")
            if raw == "active":
                status = "connected"
            elif raw == "error":
                status = "reconnect_required"
            elif raw == "pending":
                status = "connection_pending"
            elif raw == "disconnected":
                status = "not_connected"
            account = row.get("display_name")
            reason = row.get("last_error")
        out.append(
            {
                "platform": plat,
                "status": status,
                "accountName": account,
                "reason": reason,
            }
        )
    return out


async def upsert_social_connection(
    db: AsyncSession,
    *,
    company_id: UUID,
    role: MembershipRole,
    platform: str,
    account_name: str,
) -> dict:
    platform = platform.strip().lower()
    if platform not in {"facebook", "instagram", "google_business"}:
        raise not_found("UNKNOWN_PLATFORM", "That social account is not supported.")
    result = await db.execute(
        select(PublishingConnection).where(
            PublishingConnection.company_id == company_id,
            PublishingConnection.platform == platform,
        )
    )
    conn = result.scalar_one_or_none()
    if conn is None:
        conn = PublishingConnection(
            company_id=company_id,
            provider="mock",
            platform=platform,
            display_name=account_name or platform,
            status=PublishingConnectionStatus.active,
        )
        db.add(conn)
    else:
        conn.display_name = account_name or conn.display_name
        conn.status = PublishingConnectionStatus.active
        conn.last_error = None
    await db.commit()
    return {
        "platform": platform,
        "status": "connected",
        "accountName": conn.display_name,
        "reason": None,
    }


async def disconnect_social(
    db: AsyncSession, *, company_id: UUID, platform: str
) -> dict:
    platform = platform.strip().lower()
    result = await db.execute(
        select(PublishingConnection).where(
            PublishingConnection.company_id == company_id,
            PublishingConnection.platform == platform,
        )
    )
    conn = result.scalar_one_or_none()
    if conn is not None:
        conn.status = PublishingConnectionStatus.disconnected
        await db.commit()
    return {
        "platform": platform,
        "status": "not_connected",
        "accountName": None,
        "reason": None,
    }


async def create_photo_session(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    category: str,
    mime_type: str,
    byte_size: int,
    filename: Optional[str],
) -> dict:
    stage = "progress" if category == "progress" else category
    payload = await job_service.create_upload_url(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        data=MediaUploadUrlRequest(
            filename=filename or f"{stage}.jpg",
            mime_type=mime_type,
            stage_label=stage,
            file_size_bytes=byte_size,
        ),
    )
    return serialize.upload_session_out(payload)


async def complete_photo(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    media_id: UUID,
    role: MembershipRole,
) -> dict:
    await job_service.complete_upload(
        db,
        company_id=company_id,
        job_id=job_id,
        role=role,
        data=MediaCompleteRequest(media_id=media_id),
        skip_existence_check=False,
    )
    media = await job_service.get_media(db, company_id, media_id)
    return serialize.media_out(media)


async def create_voice_session(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    mime_type: str,
    byte_size: int,
    duration_ms: int,
) -> dict:
    duration_seconds = max(1, int(round(duration_ms / 1000))) if duration_ms else None
    mime = (mime_type or "audio/webm").lower().split(";")[0].strip() or "audio/webm"
    ext = {
        "audio/mp4": "m4a",
        "audio/m4a": "m4a",
        "audio/x-m4a": "m4a",
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/wav": "wav",
        "audio/x-wav": "wav",
        "audio/ogg": "ogg",
        "audio/opus": "opus",
    }.get(mime, "webm")
    payload = await voice_svc.create_voice_upload_url(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        data=VoiceUploadUrlRequest(
            filename=f"voice.{ext}",
            mime_type=mime,
            file_size_bytes=byte_size,
            duration_seconds=duration_seconds,
        ),
    )
    return serialize.upload_session_out(payload)


async def complete_voice(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    media_id: UUID,
    role: MembershipRole,
) -> dict:
    voice, _job_row = await voice_svc.complete_voice_upload(
        db,
        company_id=company_id,
        job_id=job_id,
        role=role,
        data=VoiceCompleteRequest(media_id=media_id),
    )
    out = serialize.voice_as_media(voice)
    if out is None:
        raise AppError("VOICE_NOT_FOUND", "Voice upload did not produce an audio asset.", status_code=400)
    return out


async def patch_media_phone(
    db: AsyncSession,
    *,
    company_id: UUID,
    media_id: UUID,
    role: MembershipRole,
    is_favorite: Optional[bool],
    photo_category: Optional[str],
) -> dict:
    media = await job_service.get_media(db, company_id, media_id)
    if photo_category:
        await job_service.update_media(
            db,
            company_id=company_id,
            media_id=media_id,
            role=role,
            data=MediaUpdate(stage_label=photo_category),
        )
        media = await job_service.get_media(db, company_id, media_id)
    if is_favorite is not None:
        media.is_favorite = is_favorite
        await db.commit()
        media = await job_service.get_media(db, company_id, media_id)
    return serialize.media_out(media)


async def list_jobs_phone(
    db: AsyncSession,
    company_id: UUID,
    *,
    status: Optional[str],
    scope: Optional[str],
    cursor: Optional[str],
    limit: int = 20,
) -> tuple[list[Job], Optional[str]]:
    import base64
    import json

    stmt = (
        select(Job)
        .where(Job.company_id == company_id, Job.deleted_at.is_(None), Job.status != JobStatus.archived)
        .options(
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary).selectinload(VoiceSummary.audio_asset),
        )
        .order_by(Job.created_at.desc(), Job.id.desc())
    )
    if status:
        statuses = from_public(status)
        if statuses:
            stmt = stmt.where(Job.status.in_(statuses))
    if scope == "published":
        stmt = stmt.where(Job.status == JobStatus.published)
    elif scope == "current":
        stmt = stmt.where(Job.status != JobStatus.published)
    if cursor:
        try:
            raw = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            c_time = datetime.fromisoformat(raw["t"])
            c_id = UUID(raw["id"])
        except Exception as exc:
            raise AppError("INVALID_CURSOR", "Invalid pagination cursor.", status_code=400) from exc
        stmt = stmt.where((Job.created_at < c_time) | ((Job.created_at == c_time) & (Job.id < c_id)))
    stmt = stmt.limit(limit + 1)
    rows = list((await db.execute(stmt)).scalars().unique().all())
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1]
        payload = {"t": last.created_at.isoformat(), "id": str(last.id)}
        next_cursor = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        rows = rows[:limit]
    return rows, next_cursor

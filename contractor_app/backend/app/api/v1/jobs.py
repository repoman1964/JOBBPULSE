"""Jobs CRUD, submit, status, events."""

from __future__ import annotations

import base64
import json
import logging
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Query, Request
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select

from app.core.config import get_settings
from app.core.deps import CurrentAuth, DbSession
from app.core.errors import AppError
from app.integrations.storage.s3 import ObjectStorage
from app.models.enums import InternalJobStatus, PublicJobStatus
from app.models.job import Job, JobEvent, JobSubmission
from app.models.media import MediaAsset
from app.schemas.common import JobOut, ListJobsResult
from app.schemas.requests import CreateJobRequest, SubmitJobRequest, UpdateJobRequest
from app.services.job_delete import assert_can_delete_job, get_visible_job, mark_job_deleted
from app.services.job_status import assert_public_transition
from app.services.mappers import counts_from_media, has_complete_voice, job_to_out, meets_minimums
from app.tasks.pipeline import process_job_submission

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)


async def _run_pipeline_background(
    job_id: UUID, submission_id: UUID, session_factory: object | None
) -> None:
    from app.db.session import AsyncSessionLocal
    from app.services.engine import run_content_pipeline

    factory = session_factory or AsyncSessionLocal
    async with factory() as session:  # type: ignore[operator]
        try:
            await run_content_pipeline(session, job_id, submission_id)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("in-process pipeline failed job=%s", job_id)


def _enqueue_content_pipeline(
    *,
    job_id: UUID,
    submission_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
) -> None:
    """Run the same pipeline in demo and production.

    Fake/demo mode simulates in the API process so a worker is not required.
    Live mode uses Celery and falls back in-process if the broker is down.
    """
    settings = get_settings()
    if settings.provider_mode != "fake":
        try:
            process_job_submission.delay(str(job_id), str(submission_id))
            return
        except Exception:
            logger.warning("Celery unavailable; running content pipeline in-process")

    factory = getattr(request.app.state, "test_session_factory", None)
    background_tasks.add_task(
        _run_pipeline_background, job_id, submission_id, factory
    )


def _encode_cursor(created_at: datetime, job_id: UUID) -> str:
    payload = {"t": created_at.isoformat(), "id": str(job_id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        raw = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return datetime.fromisoformat(raw["t"]), UUID(raw["id"])
    except Exception as exc:
        raise AppError("invalid_cursor", "Invalid pagination cursor.", status_code=400) from exc


async def _job_media(db: DbSession, job_id: UUID, company_id: UUID) -> list[MediaAsset]:
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job_id,
            MediaAsset.company_id == company_id,
        )
    )
    return list(result.scalars().all())


def _cover_url(media: list[MediaAsset], storage: ObjectStorage) -> str | None:
    photos = [
        m
        for m in media
        if m.kind == "photo" and not m.is_deleted and m.upload_status == "complete"
    ]
    for cat in ("after", "progress", "before"):
        for m in photos:
            if m.photo_category == cat:
                key = m.thumbnail_object_key or m.preview_object_key or m.original_object_key
                if key:
                    return storage.presign_get(key)
    return None


async def _to_job_out(db: DbSession, job: Job, storage: ObjectStorage | None = None) -> JobOut:
    # UPDATE ... onupdate=now() expires timestamp columns. Reading them in the
    # mapper without a refresh raises MissingGreenlet (HTTP 500) on async SQLAlchemy.
    if sa_inspect(job).expired_attributes:
        await db.refresh(job)
    storage = storage or ObjectStorage()
    media = await _job_media(db, job.id, job.company_id)
    return job_to_out(
        job,
        counts=counts_from_media(media),
        has_voice=has_complete_voice(media),
        cover_url=_cover_url(media, storage),
    )


async def _get_job(db: DbSession, job_id: UUID, company_id: UUID) -> Job:
    return await get_visible_job(db, job_id, company_id)


@router.get("", response_model=ListJobsResult)
async def list_jobs(
    auth: CurrentAuth,
    db: DbSession,
    status: str | None = Query(default=None),
    scope: Literal["current", "published"] | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> ListJobsResult:
    stmt = select(Job).where(Job.company_id == auth.company_id, Job.deleted_at.is_(None))
    if status:
        stmt = stmt.where(Job.public_status == status)
    if scope == "published":
        stmt = stmt.where(Job.public_status == PublicJobStatus.published.value)
    elif scope == "current":
        stmt = stmt.where(Job.public_status != PublicJobStatus.published.value)
    if cursor:
        c_time, c_id = _decode_cursor(cursor)
        stmt = stmt.where(
            (Job.created_at < c_time)
            | ((Job.created_at == c_time) & (Job.id < c_id))
        )
    stmt = stmt.order_by(Job.created_at.desc(), Job.id.desc()).limit(limit + 1)
    result = await db.execute(stmt)
    rows = list(result.scalars().all())
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1]
        next_cursor = _encode_cursor(last.created_at, last.id)
        rows = rows[:limit]

    storage = ObjectStorage()
    items = [await _to_job_out(db, j, storage) for j in rows]
    return ListJobsResult(items=items, nextCursor=next_cursor)


@router.post("", response_model=JobOut, status_code=201)
async def create_job(
    body: CreateJobRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> JobOut:
    location = body.location_text or ", ".join(
        p for p in [body.city, body.region or ""] if p
    )
    job = Job(
        company_id=auth.company_id,
        created_by_contractor_id=auth.contractor_id,
        name=body.name.strip(),
        service_type=body.service_type.strip(),
        city=body.city.strip(),
        region=(body.region or "").strip(),
        location_text=location.strip(),
        internal_note=(body.internal_note or "").strip(),
        assigned_crew_member=(body.assigned_crew_member or "").strip(),
        public_status=PublicJobStatus.active.value,
        internal_status=InternalJobStatus.draft.value,
    )
    db.add(job)
    await db.flush()
    db.add(
        JobEvent(
            company_id=auth.company_id,
            job_id=job.id,
            event_type="job.created",
            actor_type="contractor",
            actor_id=auth.contractor_id,
            payload_json={"name": job.name},
        )
    )
    await db.flush()
    return await _to_job_out(db, job)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: UUID, auth: CurrentAuth, db: DbSession) -> JobOut:
    job = await _get_job(db, job_id, auth.company_id)
    return await _to_job_out(db, job)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: UUID, auth: CurrentAuth, db: DbSession) -> None:
    job = await _get_job(db, job_id, auth.company_id)
    assert_can_delete_job(job.public_status)
    mark_job_deleted(job, now=datetime.now(UTC))
    db.add(
        JobEvent(
            company_id=auth.company_id,
            job_id=job.id,
            event_type="job.deleted",
            actor_type="contractor",
            actor_id=auth.contractor_id,
            payload_json={"name": job.name},
        )
    )
    await db.flush()


@router.patch("/{job_id}", response_model=JobOut)
async def update_job(
    job_id: UUID,
    body: UpdateJobRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> JobOut:
    job = await _get_job(db, job_id, auth.company_id)
    if job.public_status in {
        PublicJobStatus.processing.value,
        PublicJobStatus.publishing.value,
        PublicJobStatus.published.value,
    }:
        raise AppError(
            "job_locked",
            "This job can no longer be edited.",
            status_code=409,
        )
    data = body.model_dump(by_alias=False, exclude_unset=True)
    for key, attr in [
        ("name", "name"),
        ("service_type", "service_type"),
        ("city", "city"),
        ("region", "region"),
        ("location_text", "location_text"),
        ("internal_note", "internal_note"),
        ("assigned_crew_member", "assigned_crew_member"),
    ]:
        if key in data and data[key] is not None:
            setattr(job, attr, data[key])
    await db.flush()
    return await _to_job_out(db, job)


@router.post("/{job_id}/submit", response_model=JobOut)
async def submit_job(
    job_id: UUID,
    body: SubmitJobRequest,
    auth: CurrentAuth,
    db: DbSession,
    request: Request,
    background_tasks: BackgroundTasks,
) -> JobOut:
    job = await _get_job(db, job_id, auth.company_id)

    # Idempotent replay
    result = await db.execute(
        select(JobSubmission).where(
            JobSubmission.job_id == job.id,
            JobSubmission.idempotency_key == body.idempotency_key,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return await _to_job_out(db, job)

    media = await _job_media(db, job.id, auth.company_id)
    counts = counts_from_media(media)
    mins = auth.company.photo_minimums_json or {}
    if not meets_minimums(counts, mins):
        raise AppError(
            "minimums_not_met",
            "Add the required Before, Progress, and After photos before submitting.",
            status_code=400,
        )
    if not has_complete_voice(media):
        raise AppError(
            "voice_required",
            "Record a short voice description before submitting.",
            status_code=400,
        )

    if job.public_status not in {
        PublicJobStatus.ready_to_finish.value,
        PublicJobStatus.active.value,
    }:
        # Allow if already processing from prior submit with different key → conflict
        if job.public_status == PublicJobStatus.processing.value:
            raise AppError(
                "already_submitted",
                "This job is already processing.",
                status_code=409,
            )
        raise AppError(
            "invalid_state",
            "This job cannot be submitted in its current state.",
            status_code=409,
        )

    voice = next(
        m
        for m in media
        if m.kind == "audio"
        and m.is_active_voice
        and not m.is_deleted
        and m.upload_status == "complete"
    )
    version = job.submission_version + 1
    snapshot = {
        "jobId": str(job.id),
        "name": job.name,
        "serviceType": job.service_type,
        "city": job.city,
        "region": job.region,
        "locationText": job.location_text,
        "counts": counts,
        "mediaIds": [str(m.id) for m in media if not m.is_deleted and m.upload_status == "complete"],
        "voiceMediaId": str(voice.id),
    }
    submission = JobSubmission(
        company_id=auth.company_id,
        job_id=job.id,
        version=version,
        voice_media_asset_id=voice.id,
        snapshot_json=snapshot,
        idempotency_key=body.idempotency_key,
        submitted_by_contractor_id=auth.contractor_id,
    )
    db.add(submission)

    assert_public_transition(job.public_status, PublicJobStatus.processing.value)
    job.public_status = PublicJobStatus.processing.value
    job.internal_status = InternalJobStatus.queued.value
    job.submission_version = version
    job.submitted_at = datetime.now(UTC)

    db.add(
        JobEvent(
            company_id=auth.company_id,
            job_id=job.id,
            event_type="job.submitted",
            actor_type="contractor",
            actor_id=auth.contractor_id,
            payload_json={"version": version, "idempotencyKey": body.idempotency_key},
        )
    )
    await db.flush()
    # Commit before the worker/background task so it can see the submission.
    await db.commit()

    _enqueue_content_pipeline(
        job_id=job.id,
        submission_id=submission.id,
        request=request,
        background_tasks=background_tasks,
    )

    return await _to_job_out(db, job)


@router.get("/{job_id}/status", response_model=JobOut)
async def job_status(job_id: UUID, auth: CurrentAuth, db: DbSession) -> JobOut:
    return await get_job(job_id, auth, db)


@router.get("/{job_id}/events")
async def job_events(job_id: UUID, auth: CurrentAuth, db: DbSession) -> list[dict]:
    await _get_job(db, job_id, auth.company_id)
    result = await db.execute(
        select(JobEvent)
        .where(JobEvent.job_id == job_id, JobEvent.company_id == auth.company_id)
        .order_by(JobEvent.created_at.asc())
    )
    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "eventType": e.event_type,
            "actorType": e.actor_type,
            "actorId": str(e.actor_id) if e.actor_id else None,
            "payload": e.payload_json,
            "createdAt": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]

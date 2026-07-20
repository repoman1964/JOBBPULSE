"""Content review service: edit, approve, reject, job approval, publish gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, forbidden, not_found
from app.core.permissions import can_approve_and_publish, can_create_jobs
from app.db.models import (
    ContentType,
    ContentVariant,
    ContentVariantStatus,
    Job,
    JobStatus,
    MembershipRole,
)
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state

SOCIAL_CONTENT_TYPES = frozenset(
    {
        ContentType.primary_social,
        ContentType.short_caption,
        ContentType.before_after,
    }
)

ACTIVE_VARIANT_STATUSES = frozenset(
    {
        ContentVariantStatus.draft,
        ContentVariantStatus.awaiting_review,
        ContentVariantStatus.approved,
        ContentVariantStatus.rejected,
    }
)

EDITABLE_STATUSES = frozenset(
    {
        ContentVariantStatus.draft,
        ContentVariantStatus.awaiting_review,
        ContentVariantStatus.rejected,
        ContentVariantStatus.approved,  # allow text tweak after approve before publish
    }
)

APPROVABLE_STATUSES = frozenset(
    {
        ContentVariantStatus.draft,
        ContentVariantStatus.awaiting_review,
        ContentVariantStatus.rejected,
    }
)


def _ensure_can_edit(role: MembershipRole) -> None:
    if not can_create_jobs(role):
        raise forbidden("You do not have permission to edit content.")


def _ensure_can_approve(role: MembershipRole) -> None:
    if not can_approve_and_publish(role):
        raise forbidden("Only managers and owners can approve or reject content.")


def effective_body(v: ContentVariant) -> str:
    """Prefer contractor edit over generated body."""
    edited = (v.body_edited or "").strip()
    if edited:
        return edited
    return v.body_generated or ""


def serialize_variant(v: ContentVariant) -> dict:
    return {
        "id": v.id,
        "job_id": v.job_id,
        "generation_run_id": v.generation_run_id,
        "content_type": v.content_type.value,
        "platform_target": v.platform_target,
        "title": v.title,
        "body_generated": v.body_generated,
        "body_edited": v.body_edited,
        "body_effective": effective_body(v),
        "call_to_action": v.call_to_action,
        "hashtags_json": v.hashtags_json,
        "status": v.status.value,
        "version_number": v.version_number,
        "approved_by": v.approved_by,
        "approved_at": v.approved_at,
        "rejected_at": v.rejected_at,
        "created_at": v.created_at,
        "updated_at": v.updated_at,
    }


@dataclass
class ApprovalReadiness:
    can_approve_job: bool
    blockers: list[str] = field(default_factory=list)
    soft_warnings: list[str] = field(default_factory=list)
    social_approved: bool = False
    directory_approved: bool = False
    after_count: int = 0
    before_count: int = 0

    def as_dict(self) -> dict:
        return {
            "can_approve_job": self.can_approve_job,
            "blockers": list(self.blockers),
            "soft_warnings": list(self.soft_warnings),
            "social_approved": self.social_approved,
            "directory_approved": self.directory_approved,
            "after_count": self.after_count,
            "before_count": self.before_count,
        }


def evaluate_job_approval(
    job: Job,
    variants: list[ContentVariant],
    counts: job_state.PhotoCounts,
) -> ApprovalReadiness:
    """MVP approval rules (product override of build-spec §15.3).

    Hard: ≥1 after, ≥1 social-ish approved, directory_listing approved.
    Soft: missing befores never block.
    """
    blockers: list[str] = []
    soft: list[str] = []

    active = [v for v in variants if v.status != ContentVariantStatus.superseded]

    social_approved = any(
        v.status == ContentVariantStatus.approved and v.content_type in SOCIAL_CONTENT_TYPES
        for v in active
    )
    directory_approved = any(
        v.status == ContentVariantStatus.approved
        and v.content_type == ContentType.directory_listing
        for v in active
    )

    if counts.after < 1:
        blockers.append("At least one after photo is required before approving this job.")
    if not social_approved:
        blockers.append(
            "Approve at least one social variant (primary post, short caption, or before/after)."
        )
    if not directory_approved:
        blockers.append("Approve the directory listing before marking the job approved.")

    if counts.before < 1:
        soft.append(job_state.OPTIONAL_BEFORE_TIP)

    if job.status == JobStatus.archived:
        blockers.append("Archived jobs cannot be approved.")
    if job.status == JobStatus.generating:
        blockers.append("Wait for generation to finish before approving.")

    return ApprovalReadiness(
        can_approve_job=len(blockers) == 0,
        blockers=blockers,
        soft_warnings=soft,
        social_approved=social_approved,
        directory_approved=directory_approved,
        after_count=counts.after,
        before_count=counts.before,
    )


def assert_job_publishable(
    job: Job,
    variants: list[ContentVariant],
    counts: job_state.PhotoCounts,
) -> None:
    """Gate for Phases 6–7. Nothing publishes without contractor approval."""
    if job.status != JobStatus.approved:
        raise AppError(
            "PUBLISH_NOT_ALLOWED",
            "Job must be approved by a contractor before publishing.",
            status_code=400,
            details={"job_status": job.status.value},
        )
    readiness = evaluate_job_approval(job, variants, counts)
    if not readiness.can_approve_job:
        raise AppError(
            "PUBLISH_NOT_ALLOWED",
            "Approved job no longer meets publish requirements.",
            status_code=400,
            details={"blockers": readiness.blockers},
        )
    # Ensure required variants still approved (stale approved job guard)
    active = [v for v in variants if v.status != ContentVariantStatus.superseded]
    if not any(
        v.status == ContentVariantStatus.approved and v.content_type in SOCIAL_CONTENT_TYPES
        for v in active
    ):
        raise AppError(
            "PUBLISH_NOT_ALLOWED",
            "No approved social content is available to publish.",
            status_code=400,
        )
    if not any(
        v.status == ContentVariantStatus.approved
        and v.content_type == ContentType.directory_listing
        for v in active
    ):
        raise AppError(
            "PUBLISH_NOT_ALLOWED",
            "No approved directory listing is available to publish.",
            status_code=400,
        )


async def _load_job(
    db: AsyncSession, company_id: UUID, job_id: UUID, *, with_media: bool = True
) -> Job:
    opts = [selectinload(Job.content_variants)]
    if with_media:
        opts.append(selectinload(Job.media_assets))
        opts.append(selectinload(Job.voice_summary))
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.company_id == company_id).options(*opts)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise not_found("JOB_NOT_FOUND", "Job not found.")
    return job


async def _load_variant(
    db: AsyncSession, company_id: UUID, content_id: UUID
) -> tuple[ContentVariant, Job]:
    result = await db.execute(
        select(ContentVariant)
        .join(Job, Job.id == ContentVariant.job_id)
        .where(ContentVariant.id == content_id, Job.company_id == company_id)
        .options(
            selectinload(ContentVariant.job).selectinload(Job.media_assets),
            selectinload(ContentVariant.job).selectinload(Job.voice_summary),
            selectinload(ContentVariant.job).selectinload(Job.content_variants),
        )
    )
    variant = result.scalar_one_or_none()
    if variant is None:
        raise not_found("CONTENT_NOT_FOUND", "Content variant not found.")
    return variant, variant.job


def _photo_counts(job: Job) -> job_state.PhotoCounts:
    return job_state.count_photos(job_service._ready_media(job))


def _active_variants(job: Job) -> list[ContentVariant]:
    return [
        v
        for v in (job.content_variants or [])
        if v.status != ContentVariantStatus.superseded
    ]


def _clear_job_approval(job: Job) -> None:
    job.approved_at = None
    if job.status == JobStatus.approved:
        job.status = JobStatus.awaiting_review


async def get_variant(db: AsyncSession, company_id: UUID, content_id: UUID) -> dict:
    variant, _job = await _load_variant(db, company_id, content_id)
    return serialize_variant(variant)


async def update_variant(
    db: AsyncSession,
    *,
    company_id: UUID,
    content_id: UUID,
    role: MembershipRole,
    body_edited: Optional[str] = None,
    title: Optional[str] = None,
    call_to_action: Optional[str] = None,
    hashtags_json: Optional[list] = None,
    fields_set: set[str] | None = None,
) -> dict:
    _ensure_can_edit(role)
    variant, job = await _load_variant(db, company_id, content_id)

    if variant.status == ContentVariantStatus.superseded:
        raise AppError(
            "CONTENT_SUPERSEDED",
            "This content version was superseded. Edit the current draft instead.",
            status_code=400,
        )
    if variant.status not in EDITABLE_STATUSES:
        raise AppError(
            "CONTENT_NOT_EDITABLE",
            f"Content in status '{variant.status.value}' cannot be edited.",
            status_code=400,
        )

    set_fields = fields_set or set()

    if "body_edited" in set_fields:
        if body_edited is None:
            variant.body_edited = None
        else:
            variant.body_edited = body_edited
    if "title" in set_fields and title is not None:
        variant.title = title
    if "call_to_action" in set_fields:
        variant.call_to_action = call_to_action
    if "hashtags_json" in set_fields and hashtags_json is not None:
        variant.hashtags_json = hashtags_json

    # Editing after job approval keeps job approved unless they reject/regenerate.
    await db.commit()
    await db.refresh(variant)
    return serialize_variant(variant)


async def approve_variant(
    db: AsyncSession,
    *,
    company_id: UUID,
    content_id: UUID,
    user_id: UUID,
    role: MembershipRole,
) -> dict:
    _ensure_can_approve(role)
    variant, job = await _load_variant(db, company_id, content_id)

    if variant.status == ContentVariantStatus.superseded:
        raise AppError(
            "CONTENT_SUPERSEDED",
            "Cannot approve superseded content.",
            status_code=400,
        )
    if variant.status == ContentVariantStatus.approved:
        return serialize_variant(variant)

    if variant.status not in APPROVABLE_STATUSES | {ContentVariantStatus.approved}:
        raise AppError(
            "CONTENT_NOT_APPROVABLE",
            f"Content in status '{variant.status.value}' cannot be approved.",
            status_code=400,
        )

    now = datetime.now(timezone.utc)
    variant.status = ContentVariantStatus.approved
    variant.approved_by = user_id
    variant.approved_at = now
    variant.rejected_at = None

    # If job was in revision due to rejects, move back toward review when something is approved
    if job.status == JobStatus.revision_requested:
        remaining_rejects = any(
            v.status == ContentVariantStatus.rejected
            for v in _active_variants(job)
            if v.id != variant.id
        )
        if not remaining_rejects:
            job.status = JobStatus.awaiting_review

    await db.commit()
    await db.refresh(variant)
    return serialize_variant(variant)


async def reject_variant(
    db: AsyncSession,
    *,
    company_id: UUID,
    content_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    reason: Optional[str] = None,
) -> dict:
    _ensure_can_approve(role)
    variant, job = await _load_variant(db, company_id, content_id)

    if variant.status == ContentVariantStatus.superseded:
        raise AppError(
            "CONTENT_SUPERSEDED",
            "Cannot reject superseded content.",
            status_code=400,
        )
    if variant.status == ContentVariantStatus.rejected:
        return serialize_variant(variant)

    now = datetime.now(timezone.utc)
    variant.status = ContentVariantStatus.rejected
    variant.rejected_at = now
    variant.approved_by = None
    variant.approved_at = None
    # reason not persisted as a column in MVP; ignore or could log later
    _ = reason
    _ = user_id

    # Rejecting any piece pulls job out of approved and into revision
    _clear_job_approval(job)
    if job.status in {
        JobStatus.awaiting_review,
        JobStatus.approved,
        JobStatus.revision_requested,
    }:
        job.status = JobStatus.revision_requested

    await db.commit()
    await db.refresh(variant)
    return serialize_variant(variant)


async def get_approval_readiness(
    db: AsyncSession, company_id: UUID, job_id: UUID
) -> dict:
    job = await _load_job(db, company_id, job_id)
    counts = _photo_counts(job)
    readiness = evaluate_job_approval(job, list(job.content_variants or []), counts)
    return readiness.as_dict()


async def approve_all(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
) -> dict:
    """Approve all current non-superseded, non-already-approved variants, then job if rules pass."""
    _ensure_can_approve(role)
    job = await _load_job(db, company_id, job_id)

    if job.status == JobStatus.archived:
        raise AppError("JOB_ARCHIVED", "Cannot approve an archived job.", status_code=400)
    if job.status == JobStatus.generating:
        raise AppError(
            "GENERATION_IN_PROGRESS",
            "Wait for generation to finish.",
            status_code=409,
        )

    now = datetime.now(timezone.utc)
    active = _active_variants(job)
    for v in active:
        if v.status in APPROVABLE_STATUSES:
            v.status = ContentVariantStatus.approved
            v.approved_by = user_id
            v.approved_at = now
            v.rejected_at = None

    await db.flush()

    counts = _photo_counts(job)
    readiness = evaluate_job_approval(job, list(job.content_variants or []), counts)

    if readiness.can_approve_job:
        job.status = JobStatus.approved
        job.approved_at = now
    else:
        # Variants may all be approved but hard media rules fail
        if job.status not in {JobStatus.awaiting_review, JobStatus.revision_requested}:
            job.status = JobStatus.awaiting_review
        job.approved_at = None

    await db.commit()

    job_out = await job_service.get_job(db, company_id, job_id)
    # reload variants
    job_full = await _load_job(db, company_id, job_id)
    return {
        "job": job_service.serialize_job_detail(job_out),
        "variants": [serialize_variant(v) for v in _active_variants(job_full)],
        "readiness": evaluate_job_approval(
            job_full, list(job_full.content_variants or []), _photo_counts(job_full)
        ).as_dict(),
    }


async def approve_job(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
) -> dict:
    """Mark job approved only when MVP rules already satisfied (does not auto-approve variants)."""
    _ensure_can_approve(role)
    job = await _load_job(db, company_id, job_id)

    if job.status == JobStatus.archived:
        raise AppError("JOB_ARCHIVED", "Cannot approve an archived job.", status_code=400)

    counts = _photo_counts(job)
    readiness = evaluate_job_approval(job, list(job.content_variants or []), counts)

    if not readiness.can_approve_job:
        raise AppError(
            "APPROVAL_RULES_NOT_MET",
            "Job cannot be approved yet.",
            status_code=400,
            details={"blockers": readiness.blockers, "soft_warnings": readiness.soft_warnings},
        )

    now = datetime.now(timezone.utc)
    job.status = JobStatus.approved
    job.approved_at = now
    _ = user_id

    await db.commit()

    job_out = await job_service.get_job(db, company_id, job_id)
    job_full = await _load_job(db, company_id, job_id)
    return {
        "job": job_service.serialize_job_detail(job_out),
        "variants": [serialize_variant(v) for v in _active_variants(job_full)],
        "readiness": evaluate_job_approval(
            job_full, list(job_full.content_variants or []), _photo_counts(job_full)
        ).as_dict(),
    }

"""Orchestrate AI generation: readiness, snapshots, persist run + variants."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, forbidden, not_found
from app.core.permissions import can_create_jobs
from app.db.models import (
    Company,
    ContentType,
    ContentVariant,
    ContentVariantStatus,
    GenerationRun,
    GenerationRunStatus,
    GenerationType,
    Job,
    JobStatus,
    JobStructuredDetails,
    MembershipRole,
)
from app.modules.ai_generation import get_generation_provider
from app.modules.ai_generation.schemas import (
    GenerateRequest,
    GeneratedContentBundle,
    JobGenerationInput,
)
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state
from app.modules.jobs.privacy import (
    assert_title_not_in_generation_payload,
    fields_for_generation,
    transcript_for_generation,
)
from app.modules.notifications import service as notification_service

REQUIRED_CONTENT_TYPES = (
    ContentType.primary_social,
    ContentType.short_caption,
    ContentType.before_after,
    ContentType.directory_listing,
)


def _ensure_can_generate(role: MembershipRole) -> None:
    if not can_create_jobs(role):
        raise forbidden("You do not have permission to generate content for jobs.")


async def _load_job_with_company(
    db: AsyncSession, company_id: UUID, job_id: UUID
) -> Job:
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id, Job.company_id == company_id)
        .options(
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary),
            selectinload(Job.company),
            selectinload(Job.structured_details),
            selectinload(Job.content_variants),
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise not_found("JOB_NOT_FOUND", "Job not found.")
    return job


async def _has_processing_run(db: AsyncSession, job_id: UUID) -> bool:
    result = await db.execute(
        select(GenerationRun.id)
        .where(
            GenerationRun.job_id == job_id,
            GenerationRun.status == GenerationRunStatus.processing,
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


def _assert_ready_for_generation(job: Job) -> None:
    if job.status == JobStatus.archived:
        raise AppError(
            "JOB_ARCHIVED",
            "Cannot generate content for an archived job.",
            status_code=400,
        )
    counts = job_state.count_photos(job_service._ready_media(job))
    if counts.after < 1:
        raise AppError(
            "AFTER_PHOTOS_REQUIRED",
            "Add at least one after photo before generating content.",
            status_code=400,
        )
    if not job_state.has_usable_transcript(job.voice_summary):
        raise AppError(
            "TRANSCRIPT_REQUIRED",
            "A usable voice transcript is required before generating content.",
            status_code=400,
        )


def _build_input(
    job: Job,
    company: Company,
    *,
    tone: Optional[str],
    length_preference: Optional[str],
    user_instruction: Optional[str],
) -> JobGenerationInput:
    safe = fields_for_generation(job, job.voice_summary)
    transcript = transcript_for_generation(job.voice_summary)
    if not transcript:
        raise AppError(
            "TRANSCRIPT_REQUIRED",
            "A usable voice transcript is required before generating content.",
            status_code=400,
        )
    counts = job_state.count_photos(job_service._ready_media(job))
    inp = JobGenerationInput(
        job_id=str(job.id),
        company_id=str(job.company_id),
        service_key=safe.get("service_key"),
        city=safe.get("city"),
        state=safe.get("state"),
        location_display=safe.get("location_display"),
        transcript=transcript,
        before_count=counts.before,
        after_count=counts.after,
        total_photo_count=counts.total,
        company_name=company.name if company else None,
        company_trade=company.trade if company else None,
        default_tone=(company.default_tone if company else "friendly_local")
        or "friendly_local",
        default_call_to_action=company.default_call_to_action if company else None,
        tone=tone or (company.default_tone if company else None) or "friendly_local",
        length_preference=length_preference or "standard",
        user_instruction=user_instruction,
    )
    assert_title_not_in_generation_payload(inp.to_snapshot_dict())
    # Extra guard: private title string must not be a dedicated field
    snapshot = inp.to_snapshot_dict()
    if "title" in snapshot:
        raise AppError(
            "PRIVACY_VIOLATION",
            "Private job title must not appear in generation input.",
            status_code=500,
        )
    return inp


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


def serialize_run(run: GenerationRun, *, include_variants: bool = True) -> dict:
    warnings: list[str] = []
    if run.output_snapshot_json and isinstance(run.output_snapshot_json, dict):
        warnings = list(run.output_snapshot_json.get("warnings") or [])
    variants = []
    if include_variants and run.variants is not None:
        variants = [serialize_variant(v) for v in run.variants]
    return {
        "id": run.id,
        "job_id": run.job_id,
        "requested_by": run.requested_by,
        "status": run.status.value,
        "generation_type": run.generation_type.value,
        "tone": run.tone,
        "length_preference": run.length_preference,
        "user_instruction": run.user_instruction,
        "model_provider": run.model_provider,
        "model_name": run.model_name,
        "prompt_version": run.prompt_version,
        "input_snapshot_json": run.input_snapshot_json,
        "output_snapshot_json": run.output_snapshot_json,
        "error_message": run.error_message,
        "completed_at": run.completed_at,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
        "variants": variants,
        "warnings": warnings,
    }


def serialize_structured(details: JobStructuredDetails) -> dict:
    return {
        "id": details.id,
        "job_id": details.job_id,
        "generation_run_id": details.generation_run_id,
        "customer_problem": details.customer_problem,
        "work_completed": details.work_completed,
        "materials": details.materials,
        "equipment": details.equipment,
        "techniques": details.techniques,
        "challenges": details.challenges,
        "result": details.result,
        "duration_text": details.duration_text,
        "customer_reaction": details.customer_reaction,
        "homeowner_advice": details.homeowner_advice,
        "safety_notes": details.safety_notes,
        "location_context": details.location_context,
        "differentiators": details.differentiators,
        "confidence_json": details.confidence_json,
        "source_version": details.source_version,
        "created_at": details.created_at,
        "updated_at": details.updated_at,
    }


def _piece_for_type(bundle: GeneratedContentBundle, ctype: ContentType):
    key = ctype.value
    piece = bundle.content.get(key)
    if piece is None:
        raise AppError(
            "GENERATION_INCOMPLETE",
            f"Provider did not return required content type: {key}",
            status_code=500,
        )
    return piece


async def _supersede_prior_variants(db: AsyncSession, job_id: UUID) -> None:
    """Mark all prior active variants superseded, including approved (regen invalidates)."""
    result = await db.execute(
        select(ContentVariant).where(
            ContentVariant.job_id == job_id,
            ContentVariant.status.in_(
                [
                    ContentVariantStatus.draft,
                    ContentVariantStatus.awaiting_review,
                    ContentVariantStatus.rejected,
                    ContentVariantStatus.approved,
                ]
            ),
        )
    )
    for v in result.scalars().all():
        v.status = ContentVariantStatus.superseded
        v.approved_by = None
        v.approved_at = None


async def _persist_success(
    db: AsyncSession,
    *,
    job: Job,
    run: GenerationRun,
    bundle: GeneratedContentBundle,
    generation_type: GenerationType,
) -> list[ContentVariant]:
    if generation_type == GenerationType.regenerate:
        await _supersede_prior_variants(db, job.id)

    new_version = (job.generation_version or 0) + 1
    job.generation_version = new_version
    job.latest_generation_run_id = run.id
    job.status = JobStatus.awaiting_review
    # Regen always clears job-level approval — contractor must re-approve
    job.approved_at = None

    run.status = GenerationRunStatus.completed
    run.model_provider = get_generation_provider().name
    run.model_name = bundle.model_name
    run.prompt_version = bundle.prompt_version
    run.output_snapshot_json = bundle.to_snapshot_dict()
    run.completed_at = datetime.now(timezone.utc)
    run.error_message = None

    sd = bundle.structured_details
    details = job.structured_details
    if details is None:
        details = JobStructuredDetails(job_id=job.id)
        db.add(details)
        job.structured_details = details

    details.generation_run_id = run.id
    details.customer_problem = sd.customer_problem
    details.work_completed = sd.work_completed
    details.materials = sd.materials or []
    details.equipment = sd.equipment or []
    details.techniques = sd.techniques or []
    details.challenges = sd.challenges or []
    details.result = sd.result
    details.duration_text = sd.duration_text
    details.customer_reaction = sd.customer_reaction
    details.homeowner_advice = sd.homeowner_advice
    details.safety_notes = sd.safety_notes
    details.location_context = sd.location_context
    details.differentiators = sd.differentiators or []
    details.confidence_json = sd.confidence_json or {}
    details.source_version = new_version

    variants: list[ContentVariant] = []
    for ctype in REQUIRED_CONTENT_TYPES:
        piece = _piece_for_type(bundle, ctype)
        body = piece.body
        if ctype == ContentType.directory_listing and piece.summary and not body:
            body = piece.summary
        variant = ContentVariant(
            job_id=job.id,
            generation_run_id=run.id,
            content_type=ctype,
            platform_target=None,
            title=piece.title,
            body_generated=body,
            body_edited=None,
            call_to_action=piece.call_to_action,
            hashtags_json=piece.hashtags or [],
            status=ContentVariantStatus.awaiting_review,
            version_number=new_version,
        )
        db.add(variant)
        variants.append(variant)

    await db.flush()
    return variants


async def _run_generation(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    body: Optional[GenerateRequest],
    generation_type: GenerationType,
) -> dict:
    _ensure_can_generate(role)
    job = await _load_job_with_company(db, company_id, job_id)
    _assert_ready_for_generation(job)

    if await _has_processing_run(db, job_id):
        raise AppError(
            "GENERATION_IN_PROGRESS",
            "A generation run is already processing for this job.",
            status_code=409,
        )

    body = body or GenerateRequest()
    company = job.company
    if company is None:
        company = await db.get(Company, company_id)

    gen_input = _build_input(
        job,
        company,
        tone=body.tone,
        length_preference=body.length_preference,
        user_instruction=body.user_instruction,
    )
    snapshot = gen_input.to_snapshot_dict()
    assert_title_not_in_generation_payload(snapshot)

    run = GenerationRun(
        job_id=job.id,
        requested_by=user_id,
        status=GenerationRunStatus.processing,
        generation_type=generation_type,
        tone=gen_input.tone,
        length_preference=gen_input.length_preference,
        user_instruction=gen_input.user_instruction,
        model_provider=get_generation_provider().name,
        input_snapshot_json=snapshot,
    )
    db.add(run)
    job.status = JobStatus.generating
    # Leaving approved/revision while regenerating
    job.approved_at = None
    await db.flush()

    provider = get_generation_provider()
    try:
        bundle = await provider.generate_content(gen_input)
        await _persist_success(
            db,
            job=job,
            run=run,
            bundle=bundle,
            generation_type=generation_type,
        )
        await notification_service.notify_generation_complete(
            db,
            company_id=company_id,
            job_id=job.id,
            requested_by=user_id,
            success=True,
        )
        await db.commit()
    except AppError as exc:
        run.status = GenerationRunStatus.failed
        run.error_message = exc.message
        run.completed_at = datetime.now(timezone.utc)
        job.status = JobStatus.failed
        await notification_service.notify_generation_complete(
            db,
            company_id=company_id,
            job_id=job.id,
            requested_by=user_id,
            success=False,
        )
        await db.commit()
        raise
    except Exception as exc:  # noqa: BLE001 — surface as failed run
        run.status = GenerationRunStatus.failed
        run.error_message = str(exc)[:2000]
        run.completed_at = datetime.now(timezone.utc)
        job.status = JobStatus.failed
        await notification_service.notify_generation_complete(
            db,
            company_id=company_id,
            job_id=job.id,
            requested_by=user_id,
            success=False,
        )
        await db.commit()
        raise AppError(
            "GENERATION_FAILED",
            "Content generation failed. You can try again.",
            status_code=500,
            details={"error": str(exc)[:500]},
        ) from exc

    # Reload for response
    run_full = await get_run(db, company_id, run.id)
    job_out = await job_service.get_job(db, company_id, job_id)
    return {
        "run": serialize_run(run_full, include_variants=True),
        "job": job_service.serialize_job_detail(job_out),
        "variants": [serialize_variant(v) for v in run_full.variants],
        "warnings": serialize_run(run_full).get("warnings") or [],
    }


async def generate(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    body: Optional[GenerateRequest] = None,
) -> dict:
    return await _run_generation(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        body=body,
        generation_type=GenerationType.initial,
    )


async def regenerate(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: UUID,
    role: MembershipRole,
    body: Optional[GenerateRequest] = None,
) -> dict:
    """Create a new generation run. Readiness gates apply; prior variants superseded."""
    return await _run_generation(
        db,
        company_id=company_id,
        job_id=job_id,
        user_id=user_id,
        role=role,
        body=body,
        generation_type=GenerationType.regenerate,
    )


async def list_runs(
    db: AsyncSession, company_id: UUID, job_id: UUID
) -> list[GenerationRun]:
    await job_service.get_job(db, company_id, job_id)
    result = await db.execute(
        select(GenerationRun)
        .where(GenerationRun.job_id == job_id)
        .options(selectinload(GenerationRun.variants))
        .order_by(GenerationRun.created_at.desc())
    )
    # Ensure job belongs to company (get_job already did)
    runs = list(result.scalars().unique().all())
    # Filter: only runs for this company (via job check above)
    return runs


async def get_run(
    db: AsyncSession, company_id: UUID, run_id: UUID
) -> GenerationRun:
    result = await db.execute(
        select(GenerationRun)
        .join(Job, Job.id == GenerationRun.job_id)
        .where(GenerationRun.id == run_id, Job.company_id == company_id)
        .options(selectinload(GenerationRun.variants))
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise not_found("GENERATION_RUN_NOT_FOUND", "Generation run not found.")
    return run


async def get_job_content(db: AsyncSession, company_id: UUID, job_id: UUID) -> dict:
    job = await _load_job_with_company(db, company_id, job_id)
    result = await db.execute(
        select(ContentVariant)
        .where(
            ContentVariant.job_id == job_id,
            ContentVariant.status != ContentVariantStatus.superseded,
        )
        .order_by(ContentVariant.version_number.desc(), ContentVariant.created_at.desc())
    )
    variants = list(result.scalars().all())
    structured = None
    if job.structured_details is not None:
        structured = serialize_structured(job.structured_details)
    return {
        "job_id": job.id,
        "structured_details": structured,
        "variants": [serialize_variant(v) for v in variants],
        "latest_generation_run_id": job.latest_generation_run_id,
        "generation_version": job.generation_version,
    }

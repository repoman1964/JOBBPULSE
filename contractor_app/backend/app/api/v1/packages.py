"""Content packages, revisions, and approve-and-publish."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentAuth, DbSession
from app.core.errors import AppError
from app.models.content import (
    ContentPackage,
    GeneratedAsset,
    GeneratedAssetVersion,
    RevisionRequest,
)
from app.models.enums import (
    AssetStatus,
    InternalJobStatus,
    PackageStatus,
    PublicJobStatus,
    RevisionChangeType,
    RevisionStatus,
)
from app.models.job import Job, JobEvent
from app.models.media import MediaAsset
from app.schemas.common import ContentPackageOut, GeneratedAssetOut, JobOut
from app.schemas.requests import (
    ApprovePublishRequest,
    AssetRevisionRequest,
    DescriptionRevisionRequest,
    FeaturedMediaRequest,
    SelectVersionRequest,
)
from app.services.job_delete import get_visible_job
from app.services.job_status import assert_public_transition
from app.services.mappers import asset_to_out, package_to_out
from app.tasks.pipeline import process_approve_and_publish, process_revision

router = APIRouter(tags=["packages"])


async def _get_job(db: DbSession, job_id: UUID, company_id: UUID) -> Job:
    return await get_visible_job(db, job_id, company_id)


async def _latest_package(
    db: DbSession, job_id: UUID, company_id: UUID
) -> ContentPackage | None:
    result = await db.execute(
        select(ContentPackage)
        .where(
            ContentPackage.job_id == job_id,
            ContentPackage.company_id == company_id,
        )
        .options(
            selectinload(ContentPackage.assets).selectinload(GeneratedAsset.versions)
        )
        .order_by(ContentPackage.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/jobs/{job_id}/package", response_model=ContentPackageOut | None)
async def get_package(
    job_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> ContentPackageOut | None:
    await _get_job(db, job_id, auth.company_id)
    package = await _latest_package(db, job_id, auth.company_id)
    if package is None:
        return None
    return package_to_out(package)


@router.patch("/jobs/{job_id}/package/featured-media", response_model=ContentPackageOut)
async def update_featured_media(
    job_id: UUID,
    body: FeaturedMediaRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> ContentPackageOut:
    job = await _get_job(db, job_id, auth.company_id)
    if job.public_status not in {
        PublicJobStatus.ready_for_approval.value,
        PublicJobStatus.needs_revision.value,
    }:
        raise AppError("invalid_state", "Featured photos can only be changed while reviewing.")

    package = await _latest_package(db, job_id, auth.company_id)
    if package is None:
        raise AppError("not_found", "No content package yet.", status_code=404)

    for media_id, label in [
        (body.featured_before_media_id, "before"),
        (body.featured_after_media_id, "after"),
    ]:
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == media_id,
                MediaAsset.job_id == job_id,
                MediaAsset.company_id == auth.company_id,
                MediaAsset.is_deleted.is_(False),
            )
        )
        if result.scalar_one_or_none() is None:
            raise AppError("not_found", f"Selected {label} photo not found.", status_code=404)

    package.featured_before_media_id = body.featured_before_media_id
    package.featured_after_media_id = body.featured_after_media_id
    await db.flush()
    package = await _latest_package(db, job_id, auth.company_id)
    assert package is not None
    return package_to_out(package)


@router.post(
    "/jobs/{job_id}/package/description-revision",
    response_model=ContentPackageOut,
)
async def request_description_revision(
    job_id: UUID,
    body: DescriptionRevisionRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> ContentPackageOut:
    job = await _get_job(db, job_id, auth.company_id)
    package = await _latest_package(db, job_id, auth.company_id)
    if package is None:
        raise AppError("not_found", "No content package yet.", status_code=404)

    rev = RevisionRequest(
        company_id=auth.company_id,
        job_id=job.id,
        generated_asset_id=None,
        change_type=RevisionChangeType.description.value,
        instruction_text=body.instruction_text,
        status=RevisionStatus.pending.value,
        requested_by_contractor_id=auth.contractor_id,
    )
    db.add(rev)

    assert_public_transition(job.public_status, PublicJobStatus.needs_revision.value)
    job.public_status = PublicJobStatus.needs_revision.value
    job.internal_status = InternalJobStatus.revision_requested.value
    package.status = PackageStatus.revision_requested.value

    db.add(
        JobEvent(
            company_id=auth.company_id,
            job_id=job.id,
            event_type="package.description_revision_requested",
            actor_type="contractor",
            actor_id=auth.contractor_id,
            payload_json={},
        )
    )
    await db.flush()

    try:
        process_revision.delay(str(rev.id))
    except Exception:
        # Synchronous fake fallback for local without worker
        from app.services.engine import apply_description_revision

        await apply_description_revision(db, rev.id)

    package = await _latest_package(db, job_id, auth.company_id)
    assert package is not None
    return package_to_out(package)


@router.get("/jobs/{job_id}/generated-assets", response_model=list[GeneratedAssetOut])
async def list_generated_assets(
    job_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> list[GeneratedAssetOut]:
    package = await _latest_package(db, job_id, auth.company_id)
    if package is None:
        return []
    return [asset_to_out(a) for a in package.assets]


@router.get("/generated-assets/{asset_id}", response_model=GeneratedAssetOut)
async def get_generated_asset(
    asset_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> GeneratedAssetOut:
    result = await db.execute(
        select(GeneratedAsset)
        .where(
            GeneratedAsset.id == asset_id,
            GeneratedAsset.company_id == auth.company_id,
        )
        .options(selectinload(GeneratedAsset.versions))
    )
    asset = result.scalar_one_or_none()
    if asset is None:
        raise AppError("not_found", "Content asset not found.", status_code=404)
    return asset_to_out(asset)


@router.post(
    "/generated-assets/{asset_id}/revisions",
    response_model=GeneratedAssetOut,
)
async def request_asset_revision(
    asset_id: UUID,
    body: AssetRevisionRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> GeneratedAssetOut:
    result = await db.execute(
        select(GeneratedAsset)
        .where(
            GeneratedAsset.id == asset_id,
            GeneratedAsset.company_id == auth.company_id,
        )
        .options(selectinload(GeneratedAsset.versions))
    )
    asset = result.scalar_one_or_none()
    if asset is None:
        raise AppError("not_found", "Content asset not found.", status_code=404)

    result = await db.execute(
        select(ContentPackage).where(ContentPackage.id == asset.package_id)
    )
    package = result.scalar_one()
    job = await _get_job(db, package.job_id, auth.company_id)

    rev = RevisionRequest(
        company_id=auth.company_id,
        job_id=job.id,
        generated_asset_id=asset.id,
        change_type=body.change_type,
        instruction_text=body.instruction_text,
        selected_media_ids_json=(
            [str(i) for i in body.selected_media_ids] if body.selected_media_ids else None
        ),
        status=RevisionStatus.pending.value,
        requested_by_contractor_id=auth.contractor_id,
    )
    db.add(rev)
    asset.status = AssetStatus.regenerating.value
    assert_public_transition(job.public_status, PublicJobStatus.needs_revision.value)
    job.public_status = PublicJobStatus.needs_revision.value
    job.internal_status = InternalJobStatus.revision_requested.value
    await db.flush()

    try:
        process_revision.delay(str(rev.id))
    except Exception:
        from app.services.engine import apply_asset_revision

        await apply_asset_revision(db, rev.id)

    result = await db.execute(
        select(GeneratedAsset)
        .where(GeneratedAsset.id == asset_id)
        .options(selectinload(GeneratedAsset.versions))
    )
    asset = result.scalar_one()
    return asset_to_out(asset)


@router.post(
    "/generated-assets/{asset_id}/select-version",
    response_model=GeneratedAssetOut,
)
async def select_asset_version(
    asset_id: UUID,
    body: SelectVersionRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> GeneratedAssetOut:
    result = await db.execute(
        select(GeneratedAsset)
        .where(
            GeneratedAsset.id == asset_id,
            GeneratedAsset.company_id == auth.company_id,
        )
        .options(selectinload(GeneratedAsset.versions))
    )
    asset = result.scalar_one_or_none()
    if asset is None:
        raise AppError("not_found", "Content asset not found.", status_code=404)

    version = next((v for v in asset.versions if v.id == body.version_id), None)
    if version is None:
        raise AppError("not_found", "Version not found.", status_code=404)

    asset.active_version_id = version.id
    asset.title = version.title
    asset.body = version.body
    asset.preview_json = version.preview_json
    asset.payload_json = version.payload_json
    asset.status = AssetStatus.ready.value
    await db.flush()
    return asset_to_out(asset)


@router.post("/jobs/{job_id}/approve-and-publish", response_model=JobOut)
async def approve_and_publish(
    job_id: UUID,
    body: ApprovePublishRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> JobOut:
    from app.api.v1.jobs import _to_job_out

    job = await _get_job(db, job_id, auth.company_id)
    if job.public_status == PublicJobStatus.publishing.value:
        # Idempotent-ish: already publishing
        return await _to_job_out(db, job)
    if job.public_status not in {
        PublicJobStatus.ready_for_approval.value,
        PublicJobStatus.needs_revision.value,
        PublicJobStatus.publish_issue.value,
    }:
        raise AppError(
            "invalid_state",
            "Approve is only available when content is ready for review.",
            status_code=409,
        )

    package = await _latest_package(db, job_id, auth.company_id)
    if package is None:
        raise AppError("not_found", "No content package to publish.", status_code=404)

    assert_public_transition(
        job.public_status
        if job.public_status != PublicJobStatus.publish_issue.value
        else PublicJobStatus.publishing.value,
        PublicJobStatus.publishing.value,
    ) if job.public_status != PublicJobStatus.publish_issue.value else None

    job.public_status = PublicJobStatus.publishing.value
    job.internal_status = InternalJobStatus.publishing.value
    job.approved_at = datetime.now(UTC)
    package.status = PackageStatus.publishing.value

    db.add(
        JobEvent(
            company_id=auth.company_id,
            job_id=job.id,
            event_type="job.approve_and_publish",
            actor_type="contractor",
            actor_id=auth.contractor_id,
            payload_json={"idempotencyKey": body.idempotency_key},
        )
    )
    await db.flush()

    try:
        process_approve_and_publish.delay(
            str(job.id), str(package.id), body.idempotency_key
        )
    except Exception:
        from app.services.engine import apply_publish

        await apply_publish(db, job.id, package.id, body.idempotency_key)

    return await _to_job_out(db, job)

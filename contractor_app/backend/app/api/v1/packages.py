"""Content packages, revisions, and approve-and-publish."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.deps import CurrentAuth, DbSession
from app.core.errors import AppError
from app.integrations.storage.s3 import ObjectStorage
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
logger = logging.getLogger(__name__)


async def _run_publish_background(
    job_id: UUID,
    package_id: UUID,
    idempotency_key: str,
    session_factory: object | None,
) -> None:
    from app.db.session import AsyncSessionLocal
    from app.services.engine import apply_publish

    factory = session_factory or AsyncSessionLocal
    async with factory() as session:  # type: ignore[operator]
        try:
            await apply_publish(session, job_id, package_id, idempotency_key)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("in-process publish failed job=%s", job_id)


def _enqueue_publish(
    *,
    job_id: UUID,
    package_id: UUID,
    idempotency_key: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> None:
    """Run the same publisher in demo and production.

    Fake/demo mode publishes in the API process so a worker is not required.
    Live mode uses Celery and falls back in-process if the broker is down.
    """
    settings = get_settings()
    if settings.provider_mode != "fake":
        try:
            process_approve_and_publish.delay(
                str(job_id), str(package_id), idempotency_key
            )
            return
        except Exception:
            logger.warning("Celery unavailable; publishing in-process")

    factory = getattr(request.app.state, "test_session_factory", None)
    background_tasks.add_task(
        _run_publish_background, job_id, package_id, idempotency_key, factory
    )


async def _get_job(db: DbSession, job_id: UUID, company_id: UUID) -> Job:
    return await get_visible_job(db, job_id, company_id)


def _media_preview_url(media: MediaAsset, storage: ObjectStorage) -> str | None:
    key = media.thumbnail_object_key or media.preview_object_key or media.original_object_key
    if not key:
        return None
    return storage.presign_get(key)


async def _preview_urls(db: DbSession, package: ContentPackage) -> dict[str, str | None]:
    storage = ObjectStorage()
    urls: dict[str, str | None] = {"beforeUrl": None, "afterUrl": None, "coverUrl": None}
    for media_id, field in (
        (package.featured_before_media_id, "beforeUrl"),
        (package.featured_after_media_id, "afterUrl"),
    ):
        if media_id is None:
            continue
        media = await db.get(MediaAsset, media_id)
        if media is None:
            continue
        urls[field] = _media_preview_url(media, storage)
    urls["coverUrl"] = urls["afterUrl"] or urls["beforeUrl"]
    return urls


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
    return package_to_out(package, preview_urls=await _preview_urls(db, package))


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
    return package_to_out(package, preview_urls=await _preview_urls(db, package))


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
    return package_to_out(package, preview_urls=await _preview_urls(db, package))


@router.get("/jobs/{job_id}/generated-assets", response_model=list[GeneratedAssetOut])
async def list_generated_assets(
    job_id: UUID,
    auth: CurrentAuth,
    db: DbSession,
) -> list[GeneratedAssetOut]:
    package = await _latest_package(db, job_id, auth.company_id)
    if package is None:
        return []
    urls = await _preview_urls(db, package)
    return [asset_to_out(a, preview_urls=urls) for a in package.assets]


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
    package = await db.get(ContentPackage, asset.package_id)
    urls = await _preview_urls(db, package) if package else None
    return asset_to_out(asset, preview_urls=urls)


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
    urls = await _preview_urls(db, package)
    return asset_to_out(asset, preview_urls=urls)


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
    package = await db.get(ContentPackage, asset.package_id)
    urls = await _preview_urls(db, package) if package else None
    return asset_to_out(asset, preview_urls=urls)


@router.post("/jobs/{job_id}/approve-and-publish", response_model=JobOut)
async def approve_and_publish(
    job_id: UUID,
    body: ApprovePublishRequest,
    auth: CurrentAuth,
    db: DbSession,
    request: Request,
    background_tasks: BackgroundTasks,
) -> JobOut:
    from app.api.v1.jobs import _to_job_out

    job = await _get_job(db, job_id, auth.company_id)
    if job.public_status == PublicJobStatus.publishing.value:
        package = await _latest_package(db, job_id, auth.company_id)
        if package is not None:
            _enqueue_publish(
                job_id=job.id,
                package_id=package.id,
                idempotency_key=body.idempotency_key,
                request=request,
                background_tasks=background_tasks,
            )
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
    # Commit before the worker/background task so it can see publishing,
    # and so this request cannot overwrite a finished publish.
    await db.commit()

    _enqueue_publish(
        job_id=job.id,
        package_id=package.id,
        idempotency_key=body.idempotency_key,
        request=request,
        background_tasks=background_tasks,
    )

    return await _to_job_out(db, job)

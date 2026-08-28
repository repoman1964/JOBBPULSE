"""JobbPulse Engine pipeline (sync helpers used by Celery tasks and fallbacks)."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings

from app.models.company import Company
from app.models.content import (
    ContentPackage,
    GeneratedAsset,
    GeneratedAssetVersion,
    RevisionRequest,
)
from app.models.enums import (
    AssetStatus,
    DestinationType,
    InternalJobStatus,
    PackageStatus,
    PublicJobStatus,
    PublicationStatus,
    RevisionStatus,
)
from app.models.job import Job, JobEvent, JobSubmission
from app.models.media import MediaAsset
from app.models.social import PublicationAttempt, SocialConnection
from app.publishers.base import PublishResult
from app.publishers.conversion import ConversionSitePublisher
from app.publishers.portfolio import PortfolioSitePublisher
from app.publishers.social import FakeSocialPublisher

logger = logging.getLogger(__name__)

# First-ship Upload-Post destinations.
FIRST_SHIP_SOCIAL = (
    DestinationType.facebook.value,
    DestinationType.instagram.value,
    DestinationType.google_business.value,
)

SOCIAL_DESTINATIONS = set(FIRST_SHIP_SOCIAL)

# Always generate these reviewable social pieces, even if not connected.
# Posting still goes through the third-party publisher when a connection exists.
CORE_REVIEW_SOCIAL = (
    DestinationType.facebook.value,
    DestinationType.facebook_group.value,
    DestinationType.instagram.value,
    DestinationType.google_business.value,
)

FIRST_PARTY_DESTINATIONS = (
    DestinationType.conversion_site.value,
    DestinationType.portfolio_site.value,
)

# Relative hold time per visible stage (multiplied by pipeline_stage_delay_seconds).
_STAGE_HOLD = {
    InternalJobStatus.queued.value: 0.6,
    InternalJobStatus.transcribing.value: 1.1,
    InternalJobStatus.curating_media.value: 0.8,
    InternalJobStatus.generating_description.value: 1.2,
    InternalJobStatus.generating_destinations.value: 1.4,
}


def content_destinations(*, connected: set[str]) -> list[str]:
    dests = list(CORE_REVIEW_SOCIAL)
    for platform in FIRST_SHIP_SOCIAL:
        if platform in connected and platform not in dests:
            dests.append(platform)
    dests.extend(FIRST_PARTY_DESTINATIONS)
    return dests


async def _pause_stage(stage: str) -> None:
    """Hold so GET /jobs/{id} can show this stage. Demo and prod share this path."""
    seconds = get_settings().pipeline_stage_delay_seconds * _STAGE_HOLD.get(stage, 1.0)
    if seconds > 0:
        await asyncio.sleep(seconds)


async def _set_stage(
    session: AsyncSession,
    job: Job,
    status: str,
    *,
    event_type: str,
    payload: dict | None = None,
) -> None:
    job.internal_status = status
    session.add(
        JobEvent(
            company_id=job.company_id,
            job_id=job.id,
            event_type=event_type,
            actor_type="system",
            actor_id=None,
            payload_json=payload or {"internalStatus": status},
        )
    )
    await session.commit()
    await _pause_stage(status)


def _transcription_provider():
    from app.integrations.transcription.fake import FakeTranscriptionProvider

    # Live STT is a server-side swap. The contractor app always polls the same statuses.
    if get_settings().provider_mode == "live":
        logger.info("live transcription not configured; using simulated transcript")
    return FakeTranscriptionProvider()


def _content_generator():
    from app.integrations.content_gen.fake import FakeContentGenerator

    if get_settings().provider_mode == "live":
        logger.info("live content generation not configured; using simulated copy")
    return FakeContentGenerator()


async def run_content_pipeline(
    session: AsyncSession, job_id: UUID, submission_id: UUID
) -> None:
    job = await session.get(Job, job_id)
    submission = await session.get(JobSubmission, submission_id)
    if job is None or submission is None:
        logger.error("pipeline missing job/submission %s %s", job_id, submission_id)
        return

    company = await session.get(Company, job.company_id)
    if company is None:
        return

    existing = await session.execute(
        select(ContentPackage)
        .where(ContentPackage.submission_id == submission.id)
        .options(selectinload(ContentPackage.assets))
    )
    existing_pkg = existing.scalar_one_or_none()
    if existing_pkg is not None and existing_pkg.assets:
        job.public_status = PublicJobStatus.ready_for_approval.value
        job.internal_status = InternalJobStatus.ready_for_approval.value
        await session.flush()
        return

    await _pause_stage(InternalJobStatus.queued.value)

    await _set_stage(
        session,
        job,
        InternalJobStatus.transcribing.value,
        event_type="pipeline.transcribing",
    )

    result = await session.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == job.company_id,
            MediaAsset.is_deleted.is_(False),
            MediaAsset.upload_status == "complete",
        )
    )
    media = list(result.scalars().all())
    photos = [m for m in media if m.kind == "photo"]
    befores = [m for m in photos if m.photo_category == "before"]
    afters = [m for m in photos if m.photo_category == "after"]

    voice = next((m for m in media if m.kind == "audio" and m.is_active_voice), None)
    transcript = ""
    if voice:
        transcript = await _transcription_provider().transcribe(
            object_key=voice.original_object_key or "",
            mime_type=voice.mime_type,
        )

    await _set_stage(
        session,
        job,
        InternalJobStatus.curating_media.value,
        event_type="pipeline.curating_media",
    )
    featured_before = next((m for m in befores if m.is_favorite), befores[0] if befores else None)
    featured_after = next((m for m in afters if m.is_favorite), afters[0] if afters else None)

    await _set_stage(
        session,
        job,
        InternalJobStatus.generating_description.value,
        event_type="pipeline.generating_description",
    )
    generator = _content_generator()
    description = await generator.project_description(
        job_name=job.name,
        service_type=job.service_type,
        city=job.city,
        region=job.region,
        transcript=transcript,
    )

    result = await session.execute(
        select(SocialConnection).where(
            SocialConnection.company_id == job.company_id,
            SocialConnection.status == "connected",
        )
    )
    connected = {c.platform for c in result.scalars().all()}
    destinations = content_destinations(connected=connected)

    await _set_stage(
        session,
        job,
        InternalJobStatus.generating_destinations.value,
        event_type="pipeline.generating_destinations",
        payload={"destinations": destinations},
    )

    package = ContentPackage(
        company_id=job.company_id,
        job_id=job.id,
        submission_id=submission.id,
        version=submission.version,
        status=PackageStatus.ready_for_approval.value,
        project_description=description,
        featured_before_media_id=featured_before.id if featured_before else None,
        featured_after_media_id=featured_after.id if featured_after else None,
    )
    session.add(package)
    await session.flush()

    source_ids = [str(m.id) for m in [featured_before, featured_after] if m]
    provider_label = "fake" if get_settings().provider_mode != "live" else "simulated"

    for dest in destinations:
        public_name = job.service_type or "Project"
        content = await generator.destination_content(
            destination=dest,
            job_name=public_name,
            city=job.city,
            description=description,
        )
        asset = GeneratedAsset(
            company_id=job.company_id,
            package_id=package.id,
            destination_type=dest,
            title=content["title"],
            body=content["body"],
            payload_json=content.get("payload", {}),
            preview_json={
                "beforeUrl": None,
                "afterUrl": None,
                "coverUrl": None,
                **content.get("preview", {}),
            },
            status=AssetStatus.ready.value,
        )
        session.add(asset)
        await session.flush()

        version = GeneratedAssetVersion(
            generated_asset_id=asset.id,
            version=1,
            source_media_ids_json=source_ids,
            title=content["title"],
            body=content["body"],
            payload_json=content.get("payload", {}),
            preview_json=asset.preview_json,
            generation_metadata_json={
                "provider": provider_label,
                "transcriptChars": len(transcript),
            },
        )
        session.add(version)
        await session.flush()
        asset.active_version_id = version.id

    job.public_status = PublicJobStatus.ready_for_approval.value
    job.internal_status = InternalJobStatus.ready_for_approval.value
    session.add(
        JobEvent(
            company_id=job.company_id,
            job_id=job.id,
            event_type="package.ready_for_approval",
            actor_type="system",
            actor_id=None,
            payload_json={"packageId": str(package.id), "version": package.version},
        )
    )
    await session.flush()
    logger.info("pipeline complete job=%s package=%s", job.id, package.id)


async def apply_description_revision(session: AsyncSession, revision_id: UUID) -> None:
    rev = await session.get(RevisionRequest, revision_id)
    if rev is None:
        return
    rev.status = RevisionStatus.processing.value

    result = await session.execute(
        select(ContentPackage)
        .where(ContentPackage.job_id == rev.job_id)
        .options(selectinload(ContentPackage.assets).selectinload(GeneratedAsset.versions))
        .order_by(ContentPackage.version.desc())
        .limit(1)
    )
    package = result.scalar_one_or_none()
    if package is None:
        rev.status = RevisionStatus.failed.value
        return

    instruction = rev.instruction_text or rev.transcribed_instruction or ""
    new_desc = f"{package.project_description}\n\n(Updated: {instruction[:200]})".strip()
    package.project_description = new_desc

    # Bump dependent social/first-party copy lightly
    for asset in package.assets:
        next_ver = max((v.version for v in asset.versions), default=0) + 1
        version = GeneratedAssetVersion(
            generated_asset_id=asset.id,
            version=next_ver,
            source_media_ids_json=(
                asset.versions[-1].source_media_ids_json if asset.versions else []
            ),
            title=asset.title,
            body=f"{new_desc[:280]}" if asset.destination_type != "instagram" else f"{new_desc[:200]} #JobbPulse",
            payload_json=asset.payload_json,
            preview_json=asset.preview_json,
            generation_metadata_json={"revision": str(rev.id)},
        )
        session.add(version)
        await session.flush()
        asset.active_version_id = version.id
        asset.body = version.body
        asset.status = AssetStatus.ready.value

    package.status = PackageStatus.ready_for_approval.value
    job = await session.get(Job, rev.job_id)
    if job:
        job.public_status = PublicJobStatus.ready_for_approval.value
        job.internal_status = InternalJobStatus.ready_for_approval.value
    rev.status = RevisionStatus.completed.value
    await session.flush()


async def apply_asset_revision(session: AsyncSession, revision_id: UUID) -> None:
    rev = await session.get(RevisionRequest, revision_id)
    if rev is None or rev.generated_asset_id is None:
        return
    rev.status = RevisionStatus.processing.value

    result = await session.execute(
        select(GeneratedAsset)
        .where(GeneratedAsset.id == rev.generated_asset_id)
        .options(selectinload(GeneratedAsset.versions))
    )
    asset = result.scalar_one_or_none()
    if asset is None:
        rev.status = RevisionStatus.failed.value
        return

    instruction = rev.instruction_text or ""
    next_ver = max((v.version for v in asset.versions), default=0) + 1
    new_body = asset.body
    if instruction:
        new_body = f"{asset.body}\n\n({instruction[:180]})".strip()
    if rev.change_type == "photos" and rev.selected_media_ids_json:
        source_ids = rev.selected_media_ids_json
    else:
        source_ids = asset.versions[-1].source_media_ids_json if asset.versions else []

    version = GeneratedAssetVersion(
        generated_asset_id=asset.id,
        version=next_ver,
        source_media_ids_json=source_ids,
        title=asset.title,
        body=new_body,
        payload_json=asset.payload_json,
        preview_json=asset.preview_json,
        generation_metadata_json={
            "revision": str(rev.id),
            "changeType": rev.change_type,
        },
    )
    session.add(version)
    await session.flush()
    asset.active_version_id = version.id
    asset.body = new_body
    asset.status = AssetStatus.ready.value

    job = await session.get(Job, rev.job_id)
    if job:
        job.public_status = PublicJobStatus.ready_for_approval.value
        job.internal_status = InternalJobStatus.ready_for_approval.value
    rev.status = RevisionStatus.completed.value
    await session.flush()


async def apply_publish(
    session: AsyncSession,
    job_id: UUID,
    package_id: UUID,
    idempotency_key: str,
) -> None:
    job = await session.get(Job, job_id)
    result = await session.execute(
        select(ContentPackage)
        .where(ContentPackage.id == package_id)
        .options(selectinload(ContentPackage.assets).selectinload(GeneratedAsset.versions))
    )
    package = result.scalar_one_or_none()
    if job is None or package is None:
        return

    social = FakeSocialPublisher()
    conversion = ConversionSitePublisher()
    portfolio = PortfolioSitePublisher()

    failures = 0
    successes = 0

    for asset in package.assets:
        key = f"{idempotency_key}:{asset.id}:{asset.active_version_id}"
        result = await session.execute(
            select(PublicationAttempt).where(PublicationAttempt.idempotency_key == key)
        )
        existing = result.scalar_one_or_none()
        if existing and existing.status == PublicationStatus.succeeded.value:
            successes += 1
            continue

        attempt = existing or PublicationAttempt(
            company_id=job.company_id,
            job_id=job.id,
            generated_asset_id=asset.id,
            destination_type=asset.destination_type,
            provider=(
                "upload_post"
                if asset.destination_type in SOCIAL_DESTINATIONS
                else asset.destination_type
            ),
            idempotency_key=key,
            status=PublicationStatus.in_progress.value,
            request_snapshot_json={
                "title": asset.title,
                "body": asset.body,
                "destination": asset.destination_type,
            },
        )
        if existing is None:
            session.add(attempt)
            await session.flush()

        try:
            if asset.destination_type in SOCIAL_DESTINATIONS:
                pub: PublishResult = await social.publish(
                    platform=asset.destination_type,
                    title=asset.title,
                    body=asset.body,
                    media_urls=[],
                    idempotency_key=key,
                )
            elif asset.destination_type == DestinationType.conversion_site.value:
                pub = await conversion.publish(
                    company_id=job.company_id,
                    job_id=job.id,
                    title=asset.title,
                    body=asset.body,
                    package_version=package.version,
                )
            else:
                pub = await portfolio.publish(
                    company_id=job.company_id,
                    job_id=job.id,
                    title=asset.title,
                    body=asset.body,
                    package_version=package.version,
                )

            if pub.success:
                attempt.status = PublicationStatus.succeeded.value
                attempt.provider_request_id = pub.provider_request_id
                attempt.provider_job_id = pub.provider_job_id
                attempt.response_snapshot_json = pub.response or {}
                asset.status = AssetStatus.published.value
                successes += 1
            else:
                attempt.status = PublicationStatus.failed.value
                attempt.last_error_code = pub.error_code
                attempt.last_error_message = pub.error_message
                failures += 1
        except Exception as exc:
            attempt.status = PublicationStatus.failed.value
            attempt.last_error_code = "publish_exception"
            attempt.last_error_message = str(exc)[:500]
            failures += 1

    if failures == 0:
        job.public_status = PublicJobStatus.published.value
        job.internal_status = InternalJobStatus.published.value
        job.published_at = datetime.now(UTC)
        package.status = PackageStatus.published.value
    else:
        job.public_status = PublicJobStatus.publish_issue.value
        job.internal_status = InternalJobStatus.partially_failed.value
        package.status = PackageStatus.failed.value

    session.add(
        JobEvent(
            company_id=job.company_id,
            job_id=job.id,
            event_type="job.publish_finished",
            actor_type="system",
            payload_json={"successes": successes, "failures": failures},
        )
    )
    await session.flush()

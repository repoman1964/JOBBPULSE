"""Social publishing orchestration + connections (Phase 7)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.exceptions import AppError, forbidden, not_found
from app.core.permissions import can_approve_and_publish
from app.db.models import (
    ContentType,
    ContentVariant,
    ContentVariantStatus,
    Job,
    JobStatus,
    MembershipRole,
    PublicationDestinationType,
    PublicationJob,
    PublicationJobStatus,
    PublishingConnection,
    PublishingConnectionStatus,
)
from app.modules.audit import service as audit_service
from app.modules.billing import service as billing_service
from app.modules.content.service import SOCIAL_CONTENT_TYPES, assert_job_publishable
from app.modules.directory import privacy as directory_privacy
from app.modules.directory import service as directory_service
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state
from app.modules.notifications import service as notification_service
from app.modules.publishing import privacy
from app.modules.publishing.provider.base import PublishRequest, ScheduleRequest
from app.modules.publishing.provider.factory import get_publishing_provider

# First-ship Upload-Post destinations. Later platforms stay off this list.
ALLOWED_PLATFORMS = frozenset(
    {
        "facebook",
        "instagram",
        "google_business",
        "tiktok",
        "youtube",
    }
)


def _ensure_manager(role: MembershipRole) -> None:
    if not can_approve_and_publish(role):
        raise forbidden("Only managers and owners can manage publishing.")


def _provider_name() -> str:
    return (get_settings().publishing_provider or "mock").strip().lower()


async def list_connections(db: AsyncSession, company_id: UUID) -> list[dict]:
    result = await db.execute(
        select(PublishingConnection)
        .where(PublishingConnection.company_id == company_id)
        .order_by(PublishingConnection.created_at.desc())
    )
    return [privacy.serialize_connection(c) for c in result.scalars().all()]


async def start_connection(
    db: AsyncSession,
    *,
    company_id: UUID,
    role: MembershipRole,
    platform: str,
    display_name: Optional[str] = None,
) -> dict:
    _ensure_manager(role)
    platform = platform.strip().lower().replace(" ", "_")
    if platform not in ALLOWED_PLATFORMS:
        raise AppError(
            "UNSUPPORTED_PLATFORM",
            f"Platform '{platform}' is not supported.",
            status_code=400,
            details={"allowed": sorted(ALLOWED_PLATFORMS)},
        )

    provider = get_publishing_provider()
    connected = await provider.connect_account(platform=platform, display_name=display_name)
    now = datetime.now(timezone.utc)
    conn = PublishingConnection(
        company_id=company_id,
        provider=_provider_name() if _provider_name() else provider.name,
        platform=connected.platform,
        external_account_id=connected.external_account_id,
        display_name=connected.display_name,
        credentials_encrypted=connected.credentials,  # mock token; real would encrypt
        status=PublishingConnectionStatus.active,
        last_verified_at=now,
        last_error=None,
    )
    db.add(conn)
    await db.flush()  # assign conn.id before audit
    await audit_service.record_event(
        db,
        company_id=company_id,
        entity_type="publishing_connection",
        entity_id=conn.id,
        action="connection.connected",
        after={
            "platform": conn.platform,
            "display_name": conn.display_name,
            "status": conn.status.value,
            "provider": conn.provider,
        },
    )
    await db.commit()
    await db.refresh(conn)
    payload = privacy.serialize_connection(conn)
    if connected.raw and connected.raw.get("authorize_url"):
        payload["authorize_url"] = connected.raw["authorize_url"]
        payload["url"] = connected.raw["authorize_url"]
    return payload


async def connection_callback(
    db: AsyncSession,
    *,
    company_id: UUID,
    role: MembershipRole,
    connection_id: Optional[UUID] = None,
    auth_code: Optional[str] = None,
    platform: Optional[str] = None,
) -> dict:
    """OAuth callback stub — activate pending connection for mock flows."""
    _ensure_manager(role)
    _ = auth_code
    if connection_id:
        conn = await _get_connection(db, company_id, connection_id)
        if conn.status == PublishingConnectionStatus.pending:
            conn.status = PublishingConnectionStatus.active
            conn.last_verified_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(conn)
        return privacy.serialize_connection(conn)
    if platform:
        return await start_connection(
            db, company_id=company_id, role=role, platform=platform
        )
    raise AppError(
        "CALLBACK_INCOMPLETE",
        "Provide connection_id or platform to complete connection.",
        status_code=400,
    )


async def disconnect_connection(
    db: AsyncSession,
    *,
    company_id: UUID,
    connection_id: UUID,
    role: MembershipRole,
) -> dict:
    _ensure_manager(role)
    conn = await _get_connection(db, company_id, connection_id)
    before = {"status": conn.status.value, "platform": conn.platform}
    conn.status = PublishingConnectionStatus.disconnected
    conn.credentials_encrypted = None
    await audit_service.record_event(
        db,
        company_id=company_id,
        entity_type="publishing_connection",
        entity_id=conn.id,
        action="connection.disconnected",
        before=before,
        after={"status": conn.status.value, "platform": conn.platform},
    )
    await db.commit()
    await db.refresh(conn)
    return privacy.serialize_connection(conn)


async def verify_connection(
    db: AsyncSession,
    *,
    company_id: UUID,
    connection_id: UUID,
    role: MembershipRole,
) -> dict:
    _ensure_manager(role)
    conn = await _get_connection(db, company_id, connection_id)
    provider = get_publishing_provider()
    ok = await provider.verify_connection(
        platform=conn.platform,
        external_account_id=conn.external_account_id or "",
        credentials=conn.credentials_encrypted,
    )
    now = datetime.now(timezone.utc)
    if ok:
        conn.last_verified_at = now
        conn.last_error = None
        if conn.status == PublishingConnectionStatus.error:
            conn.status = PublishingConnectionStatus.active
    else:
        conn.last_error = "Verification failed"
        conn.status = PublishingConnectionStatus.error
    await db.commit()
    await db.refresh(conn)
    return privacy.serialize_connection(conn)


async def _get_connection(
    db: AsyncSession, company_id: UUID, connection_id: UUID
) -> PublishingConnection:
    result = await db.execute(
        select(PublishingConnection).where(
            PublishingConnection.id == connection_id,
            PublishingConnection.company_id == company_id,
        )
    )
    conn = result.scalar_one_or_none()
    if conn is None:
        raise not_found("CONNECTION_NOT_FOUND", "Publishing connection not found.")
    return conn


def _pick_social_variant(job: Job) -> ContentVariant:
    active = [
        v
        for v in (job.content_variants or [])
        if v.status == ContentVariantStatus.approved
        and v.content_type in SOCIAL_CONTENT_TYPES
    ]
    if not active:
        raise AppError(
            "PUBLISH_NOT_ALLOWED",
            "No approved social content is available to publish.",
            status_code=400,
        )
    # Prefer primary_social
    primary = [v for v in active if v.content_type == ContentType.primary_social]
    pool = primary or active
    pool.sort(key=lambda v: v.approved_at or v.created_at, reverse=True)
    return pool[0]


def _idempotency_key(
    job_id: UUID,
    connection_id: UUID,
    variant_id: UUID,
    version: int,
    *,
    scheduled: bool = False,
) -> str:
    kind = "sched" if scheduled else "pub"
    return f"{kind}:{job_id}:{connection_id}:{variant_id}:v{version}"


async def _load_job(db: AsyncSession, company_id: UUID, job_id: UUID) -> Job:
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id, Job.company_id == company_id)
        .options(
            selectinload(Job.content_variants),
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary),
            selectinload(Job.directory_listing),
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise not_found("JOB_NOT_FOUND", "Job not found.")
    return job


async def publish_job(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    publish_to_directory: bool = True,
    social_connection_ids: Optional[list[UUID]] = None,
    scheduled_for: Optional[datetime] = None,
) -> dict:
    """Unified Publish: directory (first-party) + social (provider)."""
    _ensure_manager(role)
    await billing_service.assert_company_can_publish(db, company_id)
    social_ids = list(social_connection_ids or [])

    if not publish_to_directory and not social_ids:
        raise AppError(
            "NOTHING_TO_PUBLISH",
            "Select at least directory or one social account to publish.",
            status_code=400,
        )

    # Scheduling uses dedicated endpoint preference; allow scheduled_for here too
    is_schedule = scheduled_for is not None

    job = await _load_job(db, company_id, job_id)
    counts = job_state.count_photos(job_service._ready_media(job))
    assert_job_publishable(job, list(job.content_variants or []), counts)

    company = await directory_service._load_company(db, company_id)
    publications: list[dict] = []
    listing_out: Optional[dict] = None

    # --- Directory (immediate even when social is scheduled) ---
    if publish_to_directory:
        listing = await directory_service._publish_directory_for_job(
            db, job=job, company=company
        )
        await db.flush()
        # Audit row (optional history)
        dir_key = f"directory:{job.id}"
        existing_dir = await db.execute(
            select(PublicationJob).where(PublicationJob.idempotency_key == dir_key)
        )
        dir_pub = existing_dir.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if dir_pub is None:
            dir_pub = PublicationJob(
                job_id=job.id,
                content_variant_id=None,
                destination_type=PublicationDestinationType.directory,
                publishing_connection_id=None,
                provider="jobpulse_directory",
                status=PublicationJobStatus.published,
                idempotency_key=dir_key,
                external_url=directory_privacy.absolute_directory_url(
                    directory_privacy.project_path(listing)
                ),
                attempt_count=1,
                published_at=now,
            )
            db.add(dir_pub)
        else:
            dir_pub.status = PublicationJobStatus.published
            dir_pub.published_at = dir_pub.published_at or now
            dir_pub.attempt_count = (dir_pub.attempt_count or 0) + 1
            dir_pub.external_url = directory_privacy.absolute_directory_url(
                directory_privacy.project_path(listing)
            )
        await db.flush()
        await db.refresh(listing)
        await db.refresh(dir_pub)
        listing_out = directory_privacy.admin_listing_payload(listing, include_media=False)
        publications.append(privacy.serialize_publication(dir_pub))
        listing_id = listing.id
        public_path = directory_privacy.project_path(listing)
        await audit_service.record_event(
            db,
            company_id=company_id,
            entity_type="job",
            entity_id=job.id,
            action="job.published",
            after={
                "destination": "directory",
                "listing_id": str(listing.id),
                "publication_id": str(dir_pub.id),
                "status": dir_pub.status.value,
            },
            private_title=job.title,
        )
        await audit_service.record_event(
            db,
            company_id=company_id,
            entity_type="publication_job",
            entity_id=dir_pub.id,
            action="publication.success",
            after={
                "destination_type": "directory",
                "status": dir_pub.status.value,
                "job_id": str(job.id),
            },
            private_title=job.title,
        )
        await notification_service.notify_directory_published(
            db,
            company_id=company_id,
            job_id=job.id,
            listing_id=listing.id,
            public_path=public_path,
        )
    else:
        listing_id = None

    # --- Social ---
    if social_ids:
        variant = _pick_social_variant(job)
        payload = privacy.build_social_payload(job, variant)
        privacy.assert_no_private_title(payload, job.title or "")
        media_urls = payload.get("media_urls") or []

        connections = await _load_active_connections(db, company_id, social_ids)
        provider = get_publishing_provider()

        for conn in connections:
            pub = await _publish_to_connection(
                db,
                job=job,
                variant=variant,
                connection=conn,
                body=payload["body"],
                title=payload.get("title"),
                media_urls=media_urls,
                metadata={
                    k: payload[k]
                    for k in ("service_key", "city", "state", "location_display", "content_type")
                    if payload.get(k) is not None
                },
                scheduled_for=scheduled_for if is_schedule else None,
                provider=provider,
            )
            await db.refresh(pub)
            publications.append(privacy.serialize_publication(pub))
            success = pub.status in {
                PublicationJobStatus.published,
                PublicationJobStatus.scheduled,
            }
            await audit_service.record_event(
                db,
                company_id=company_id,
                entity_type="publication_job",
                entity_id=pub.id,
                action="publication.success" if success else "publication.failed",
                after={
                    "destination_type": "social",
                    "platform": conn.platform,
                    "status": pub.status.value,
                    "job_id": str(job.id),
                    "last_error": pub.last_error,
                },
                private_title=job.title,
            )
            await notification_service.notify_social_publication(
                db,
                company_id=company_id,
                job_id=job.id,
                publication_id=pub.id,
                platform=conn.platform,
                success=success,
                error=pub.last_error,
            )

    now = datetime.now(timezone.utc)
    # Mark job published if anything went live (or scheduled social still counts as action)
    any_success = any(
        p.get("status") in {"published", "scheduled"} for p in publications
    )
    if any_success or publish_to_directory:
        job.status = JobStatus.published
        job.published_at = job.published_at or now
        await audit_service.record_event(
            db,
            company_id=company_id,
            entity_type="job",
            entity_id=job.id,
            action="job.published",
            after={
                "status": job.status.value,
                "destinations": [p.get("destination_type") for p in publications],
                "publication_count": len(publications),
            },
            private_title=job.title,
        )

    await db.commit()

    job_out = await job_service.get_job(db, company_id, job_id)
    if listing_out is None and listing_id is None:
        # Social-only: may still have prior listing
        job_reload = await _load_job(db, company_id, job_id)
        if job_reload.directory_listing is not None:
            listing_id = job_reload.directory_listing.id
    if listing_id is not None:
        try:
            listing_out = await directory_service.get_listing(db, company_id, listing_id)
        except Exception:  # noqa: BLE001
            pass

    result: dict = {
        "job": job_service.serialize_job_detail(job_out),
        "listing": listing_out,
        "publications": publications,
        "public_path": listing_out.get("public_path") if listing_out else None,
        "public_url": listing_out.get("public_url") if listing_out else None,
    }
    if listing_out:
        profile = await directory_service.ensure_contractor_profile(db, company)
        result["contractor_public_url"] = directory_privacy.absolute_directory_url(
            directory_privacy.contractor_path(profile, company)
        )
    return result


async def schedule_job(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
    scheduled_for: datetime,
    publish_to_directory: bool = False,
    social_connection_ids: Optional[list[UUID]] = None,
) -> dict:
    if not social_connection_ids:
        raise AppError(
            "NOTHING_TO_SCHEDULE",
            "Select at least one social connection to schedule.",
            status_code=400,
        )
    if scheduled_for.tzinfo is None:
        scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)
    if scheduled_for <= datetime.now(timezone.utc):
        raise AppError(
            "INVALID_SCHEDULE",
            "scheduled_for must be in the future.",
            status_code=400,
        )
    return await publish_job(
        db,
        company_id=company_id,
        job_id=job_id,
        role=role,
        publish_to_directory=publish_to_directory,
        social_connection_ids=social_connection_ids,
        scheduled_for=scheduled_for,
    )


async def _load_active_connections(
    db: AsyncSession, company_id: UUID, ids: list[UUID]
) -> list[PublishingConnection]:
    result = await db.execute(
        select(PublishingConnection).where(
            PublishingConnection.company_id == company_id,
            PublishingConnection.id.in_(ids),
        )
    )
    found = {c.id: c for c in result.scalars().all()}
    missing = [str(i) for i in ids if i not in found]
    if missing:
        raise not_found(
            "CONNECTION_NOT_FOUND",
            "One or more publishing connections were not found.",
        )
    active: list[PublishingConnection] = []
    for i in ids:
        conn = found[i]
        if conn.status != PublishingConnectionStatus.active:
            raise AppError(
                "CONNECTION_NOT_ACTIVE",
                f"Connection '{conn.display_name}' is not active.",
                status_code=400,
                details={"connection_id": str(conn.id), "status": conn.status.value},
            )
        active.append(conn)
    return active


async def _publish_to_connection(
    db: AsyncSession,
    *,
    job: Job,
    variant: ContentVariant,
    connection: PublishingConnection,
    body: str,
    title: Optional[str],
    media_urls: list[str],
    metadata: dict,
    scheduled_for: Optional[datetime],
    provider,
) -> PublicationJob:
    is_sched = scheduled_for is not None
    key = _idempotency_key(
        job.id,
        connection.id,
        variant.id,
        variant.version_number,
        scheduled=is_sched,
    )
    result = await db.execute(
        select(PublicationJob).where(PublicationJob.idempotency_key == key)
    )
    pub = result.scalar_one_or_none()

    # Already published successfully — do not re-post
    if pub is not None and pub.status == PublicationJobStatus.published:
        return pub
    if pub is not None and pub.status == PublicationJobStatus.scheduled and is_sched:
        return pub

    if pub is None:
        pub = PublicationJob(
            job_id=job.id,
            content_variant_id=variant.id,
            destination_type=PublicationDestinationType.social,
            publishing_connection_id=connection.id,
            provider=connection.provider or provider.name,
            scheduled_for=scheduled_for,
            status=PublicationJobStatus.processing,
            idempotency_key=key,
            attempt_count=0,
        )
        db.add(pub)
        await db.flush()

    pub.attempt_count = (pub.attempt_count or 0) + 1
    pub.status = PublicationJobStatus.processing
    pub.last_error = None
    pub.scheduled_for = scheduled_for
    await db.flush()

    req_kwargs = dict(
        platform=connection.platform,
        external_account_id=connection.external_account_id or "",
        credentials=connection.credentials_encrypted,
        body=body,
        title=title,
        media_urls=media_urls,
        metadata=metadata,
        idempotency_key=key,
    )

    if is_sched:
        result_p = await provider.schedule_post(
            ScheduleRequest(**req_kwargs, scheduled_for=scheduled_for)
        )
    else:
        result_p = await provider.publish_post(PublishRequest(**req_kwargs))

    now = datetime.now(timezone.utc)
    pub.provider_request_id = result_p.external_id
    pub.provider_response_json = result_p.raw
    pub.external_url = result_p.external_url

    if result_p.success:
        if result_p.status == "scheduled" or is_sched:
            pub.status = PublicationJobStatus.scheduled
            pub.published_at = None
        else:
            pub.status = PublicationJobStatus.published
            pub.published_at = now
        pub.last_error = None
    else:
        pub.status = PublicationJobStatus.failed
        pub.last_error = result_p.error_message or "Publish failed"
        pub.published_at = None

    await db.flush()
    return pub


async def list_publications(
    db: AsyncSession, company_id: UUID, job_id: UUID
) -> list[dict]:
    # Ensure job belongs to company
    await _load_job(db, company_id, job_id)
    result = await db.execute(
        select(PublicationJob)
        .where(PublicationJob.job_id == job_id)
        .options(selectinload(PublicationJob.connection))
        .order_by(PublicationJob.created_at.desc())
    )
    return [privacy.serialize_publication(p) for p in result.scalars().all()]


async def retry_publication(
    db: AsyncSession,
    *,
    company_id: UUID,
    publication_id: UUID,
    role: MembershipRole,
) -> dict:
    _ensure_manager(role)
    pub = await _get_publication(db, company_id, publication_id)
    if pub.status != PublicationJobStatus.failed:
        raise AppError(
            "RETRY_NOT_ALLOWED",
            "Only failed publications can be retried.",
            status_code=400,
            details={"status": pub.status.value},
        )
    if pub.destination_type != PublicationDestinationType.social:
        raise AppError(
            "RETRY_NOT_ALLOWED",
            "Only social publications support retry.",
            status_code=400,
        )
    if not pub.publishing_connection_id:
        raise AppError("RETRY_NOT_ALLOWED", "Missing connection for retry.", status_code=400)

    job = await _load_job(db, company_id, pub.job_id)
    counts = job_state.count_photos(job_service._ready_media(job))
    assert_job_publishable(job, list(job.content_variants or []), counts)

    conn = await _get_connection(db, company_id, pub.publishing_connection_id)
    if conn.status != PublishingConnectionStatus.active:
        raise AppError(
            "CONNECTION_NOT_ACTIVE",
            "Connection is not active.",
            status_code=400,
        )

    variant = None
    if pub.content_variant_id:
        for v in job.content_variants or []:
            if v.id == pub.content_variant_id:
                variant = v
                break
    if variant is None:
        variant = _pick_social_variant(job)

    payload = privacy.build_social_payload(job, variant)
    privacy.assert_no_private_title(payload, job.title or "")
    provider = get_publishing_provider()

    # Reuse same idempotency key — mock will not double-create if already published
    # Clear failed state and re-attempt
    pub.status = PublicationJobStatus.processing
    await db.flush()

    # Temporarily strip fail marker for retry tests that edit body_edited? Keep as-is.
    # For retry after fail marker: user would edit content; for tests we re-call provider
    # with same body — if still has FAIL marker, fails again. Tests can patch body.
    result_p = await provider.publish_post(
        PublishRequest(
            platform=conn.platform,
            external_account_id=conn.external_account_id or "",
            credentials=conn.credentials_encrypted,
            body=payload["body"],
            title=payload.get("title"),
            media_urls=payload.get("media_urls") or [],
            metadata={},
            idempotency_key=pub.idempotency_key,
        )
    )
    pub.attempt_count = (pub.attempt_count or 0) + 1
    pub.provider_request_id = result_p.external_id
    pub.provider_response_json = result_p.raw
    pub.external_url = result_p.external_url
    now = datetime.now(timezone.utc)
    if result_p.success:
        pub.status = PublicationJobStatus.published
        pub.published_at = now
        pub.last_error = None
    else:
        pub.status = PublicationJobStatus.failed
        pub.last_error = result_p.error_message or "Retry failed"

    await audit_service.record_event(
        db,
        company_id=company_id,
        entity_type="publication_job",
        entity_id=pub.id,
        action="publication.retry",
        after={
            "status": pub.status.value,
            "attempt_count": pub.attempt_count,
            "last_error": pub.last_error,
            "job_id": str(job.id),
        },
        private_title=job.title,
    )
    await notification_service.notify_social_publication(
        db,
        company_id=company_id,
        job_id=job.id,
        publication_id=pub.id,
        platform=conn.platform,
        success=result_p.success,
        error=pub.last_error,
    )

    await db.commit()
    await db.refresh(pub)
    return privacy.serialize_publication(pub)


async def cancel_publication(
    db: AsyncSession,
    *,
    company_id: UUID,
    publication_id: UUID,
    role: MembershipRole,
) -> dict:
    _ensure_manager(role)
    pub = await _get_publication(db, company_id, publication_id)
    if pub.status not in {
        PublicationJobStatus.scheduled,
        PublicationJobStatus.pending,
        PublicationJobStatus.processing,
    }:
        raise AppError(
            "CANCEL_NOT_ALLOWED",
            "Only scheduled or pending publications can be cancelled.",
            status_code=400,
            details={"status": pub.status.value},
        )
    pub.status = PublicationJobStatus.cancelled
    pub.last_error = None
    await db.commit()
    await db.refresh(pub)
    return privacy.serialize_publication(pub)


async def _get_publication(
    db: AsyncSession, company_id: UUID, publication_id: UUID
) -> PublicationJob:
    result = await db.execute(
        select(PublicationJob)
        .join(Job, Job.id == PublicationJob.job_id)
        .where(PublicationJob.id == publication_id, Job.company_id == company_id)
    )
    pub = result.scalar_one_or_none()
    if pub is None:
        raise not_found("PUBLICATION_NOT_FOUND", "Publication not found.")
    return pub

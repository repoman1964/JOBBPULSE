"""Directory publishing service — first-party JobPulse (not social provider)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, forbidden, not_found
from app.core.permissions import can_approve_and_publish
from app.core.slug import slugify
from app.db.models import (
    Company,
    ContentType,
    ContentVariant,
    ContentVariantStatus,
    ContractorProfile,
    DirectoryListing,
    DirectoryListingMedia,
    DirectoryListingStatus,
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipRole,
)
from app.modules.audit import service as audit_service
from app.modules.content.service import assert_job_publishable, effective_body
from app.modules.directory import privacy
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state

logger = logging.getLogger(__name__)


def _ensure_can_publish(role: MembershipRole) -> None:
    if not can_approve_and_publish(role):
        raise forbidden("Only managers and owners can publish or unpublish.")


def _ready_images(job: Job) -> list[MediaAsset]:
    return [
        m
        for m in (job.media_assets or [])
        if m.asset_type == MediaAssetType.image
        and m.processing_status != MediaProcessingStatus.pending_upload
        and m.stage_label in {MediaStageLabel.before, MediaStageLabel.after}
    ]


def _approved_directory_variant(job: Job) -> ContentVariant:
    active = [
        v
        for v in (job.content_variants or [])
        if v.status != ContentVariantStatus.superseded
        and v.content_type == ContentType.directory_listing
        and v.status == ContentVariantStatus.approved
    ]
    if not active:
        raise AppError(
            "PUBLISH_NOT_ALLOWED",
            "No approved directory listing is available to publish.",
            status_code=400,
        )
    # Prefer newest approved
    active.sort(key=lambda v: v.approved_at or v.created_at, reverse=True)
    return active[0]


def _public_title_from_variant(variant: ContentVariant, job: Job) -> str:
    title = (variant.title or "").strip()
    if title:
        return title[:300]
    # Fallback from service + city — never job.title
    parts: list[str] = []
    if job.service_key:
        parts.append(job.service_key.replace("_", " ").title())
    if job.city:
        parts.append(f"in {job.city}")
    return (" ".join(parts) if parts else "Completed project")[:300]


def _project_slug(job: Job) -> str:
    service = slugify(job.service_key or "project")[:40] or "project"
    city = slugify(job.city or "local")[:40] or "local"
    suffix = job.id.hex[:8]
    return f"{service}-{city}-{suffix}"


def _seo_for_listing(title: str, summary: str, city: Optional[str], service_key: Optional[str]) -> tuple[str, str]:
    location = city or "your area"
    service = (service_key or "home service").replace("_", " ")
    seo_title = f"{title} | {service.title()} in {location} | JobPulse"[:300]
    desc = summary.strip().replace("\n", " ")
    if len(desc) > 160:
        desc = desc[:157] + "..."
    if not desc:
        desc = f"Completed {service} project in {location}."
    return seo_title, desc[:500]


def _structured_data(
    title: str,
    summary: str,
    city: Optional[str],
    state: Optional[str],
    company_name: str,
    image_urls: list[str],
) -> dict:
    data: dict = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": title,
        "description": summary[:500] if summary else None,
        "provider": {
            "@type": "LocalBusiness",
            "name": company_name,
        },
    }
    if city or state:
        data["contentLocation"] = {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": city,
                "addressRegion": state,
            },
        }
    if image_urls:
        data["image"] = image_urls[:10]
    return data


async def _load_company(db: AsyncSession, company_id: UUID) -> Company:
    result = await db.execute(
        select(Company)
        .where(Company.id == company_id)
        .options(
            selectinload(Company.services),
            selectinload(Company.service_areas),
            selectinload(Company.contractor_profile),
        )
    )
    company = result.scalar_one_or_none()
    if company is None:
        raise not_found("COMPANY_NOT_FOUND", "Company not found.")
    return company


async def _load_job_for_publish(db: AsyncSession, company_id: UUID, job_id: UUID) -> Job:
    result = await db.execute(
        select(Job)
        .where(Job.id == job_id, Job.company_id == company_id)
        .options(
            selectinload(Job.content_variants),
            selectinload(Job.media_assets),
            selectinload(Job.voice_summary),
            selectinload(Job.directory_listing).selectinload(DirectoryListing.media_links),
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise not_found("JOB_NOT_FOUND", "Job not found.")
    return job


async def ensure_contractor_profile(
    db: AsyncSession,
    company: Company,
    *,
    auto_publish: bool = False,
) -> ContractorProfile:
    """Get or create contractor profile from company defaults. Slug is stable."""
    result = await db.execute(
        select(ContractorProfile).where(ContractorProfile.company_id == company.id)
    )
    profile = result.scalar_one_or_none()
    if profile is not None:
        if auto_publish and not profile.published:
            profile.published = True
        return profile

    base = slugify(company.slug or company.name)[:180] or "contractor"
    # company.slug already unique; reuse as public slug base for stability
    public_slug = base
    # Collision guard (rare if company slug unique)
    existing = await db.execute(
        select(ContractorProfile).where(ContractorProfile.public_slug == public_slug)
    )
    if existing.scalar_one_or_none() is not None:
        public_slug = f"{base}-{str(company.id).replace('-', '')[:8]}"

    profile = ContractorProfile(
        company_id=company.id,
        public_slug=public_slug,
        headline=company.name,
        public_description=company.description,
        contact_phone=company.phone,
        website_url=company.website_url,
        lead_form_enabled=True,
        published=auto_publish,
        seo_title=f"{company.name} | JobPulse"[:300],
        seo_description=(company.description or f"{company.name} home service contractor.")[:500],
    )
    db.add(profile)
    await db.flush()
    return profile


async def get_or_create_profile(db: AsyncSession, company_id: UUID) -> dict:
    company = await _load_company(db, company_id)
    profile = await ensure_contractor_profile(db, company)
    await db.commit()
    # Reload company without lazy loads
    company = await _load_company(db, company_id)
    profile = company.contractor_profile or profile
    return privacy.admin_profile_payload(profile, company)


async def update_profile(
    db: AsyncSession,
    company_id: UUID,
    role: MembershipRole,
    data: dict,
) -> dict:
    if not can_approve_and_publish(role):
        # Managers can edit public profile; crew cannot
        raise forbidden("Only managers and owners can edit the public contractor profile.")
    company = await _load_company(db, company_id)
    profile = await ensure_contractor_profile(db, company)
    for key, value in data.items():
        if key in {
            "headline",
            "public_description",
            "contact_phone",
            "contact_email",
            "website_url",
            "lead_form_enabled",
            "published",
            "seo_title",
            "seo_description",
        }:
            setattr(profile, key, value)
    await db.commit()
    await db.refresh(profile)
    return privacy.admin_profile_payload(profile, company)


async def list_listings(
    db: AsyncSession,
    company_id: UUID,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    result = await db.execute(
        select(DirectoryListing)
        .where(DirectoryListing.company_id == company_id)
        .options(selectinload(DirectoryListing.media_links).selectinload(DirectoryListingMedia.media_asset))
        .order_by(DirectoryListing.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    listings = list(result.scalars().all())
    return [privacy.admin_listing_payload(l) for l in listings]


async def get_listing(db: AsyncSession, company_id: UUID, listing_id: UUID) -> dict:
    listing = await _get_company_listing(db, company_id, listing_id)
    return privacy.admin_listing_payload(listing)


async def update_listing(
    db: AsyncSession,
    company_id: UUID,
    listing_id: UUID,
    role: MembershipRole,
    data: dict,
) -> dict:
    _ensure_can_publish(role)
    listing = await _get_company_listing(db, company_id, listing_id)
    for key, value in data.items():
        if key in {
            "public_title",
            "public_summary",
            "seo_title",
            "seo_description",
            "location_display",
        }:
            setattr(listing, key, value)
    await db.commit()
    await db.refresh(listing)
    return privacy.admin_listing_payload(listing)


async def _get_company_listing(
    db: AsyncSession, company_id: UUID, listing_id: UUID
) -> DirectoryListing:
    result = await db.execute(
        select(DirectoryListing)
        .where(DirectoryListing.id == listing_id, DirectoryListing.company_id == company_id)
        .options(
            selectinload(DirectoryListing.media_links).selectinload(DirectoryListingMedia.media_asset),
            selectinload(DirectoryListing.contractor_profile),
        )
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise not_found("LISTING_NOT_FOUND", "Directory listing not found.")
    return listing


async def _sync_listing_media(db: AsyncSession, listing: DirectoryListing, job: Job) -> list[str]:
    """Replace media links from job before/after images. Returns public image URLs."""
    # Clear existing links without lazy-loading the collection (async-safe)
    await db.execute(
        delete(DirectoryListingMedia).where(
            DirectoryListingMedia.directory_listing_id == listing.id
        )
    )
    await db.flush()

    images = _ready_images(job)
    # After first (display order), then before
    afters = [m for m in images if m.stage_label == MediaStageLabel.after]
    befores = [m for m in images if m.stage_label == MediaStageLabel.before]
    ordered = afters + befores

    urls: list[str] = []
    for i, media in enumerate(ordered):
        link = DirectoryListingMedia(
            directory_listing_id=listing.id,
            media_asset_id=media.id,
            stage_label=media.stage_label.value,
            display_order=i,
        )
        db.add(link)
        try:
            from app.core import storage as storage_svc

            url = storage_svc.public_or_signed_url(media.storage_key)
            if url:
                urls.append(url)
        except Exception:  # noqa: BLE001
            pass
    await db.flush()
    return urls


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
    """Unified publish entry point. Phase 6: directory only."""
    _ensure_can_publish(role)

    if social_connection_ids:
        raise AppError(
            "SOCIAL_NOT_AVAILABLE",
            "Social publishing is not available yet. Publish without social destinations for now.",
            status_code=400,
            details={"social_connection_ids": [str(x) for x in social_connection_ids]},
        )
    if scheduled_for is not None:
        raise AppError(
            "SCHEDULING_NOT_AVAILABLE",
            "Scheduled publishing is not available yet. Publish now without a schedule.",
            status_code=400,
        )
    if not publish_to_directory:
        raise AppError(
            "NOTHING_TO_PUBLISH",
            "Enable directory publishing to publish this job.",
            status_code=400,
        )

    job = await _load_job_for_publish(db, company_id, job_id)
    counts = job_state.count_photos(job_service._ready_media(job))
    assert_job_publishable(job, list(job.content_variants or []), counts)

    company = await _load_company(db, company_id)
    listing = await _publish_directory_for_job(db, job=job, company=company)

    now = datetime.now(timezone.utc)
    job.status = JobStatus.published
    job.published_at = now

    await db.commit()

    # Reload for response
    job_out = await job_service.get_job(db, company_id, job_id)
    listing_out = await get_listing(db, company_id, listing.id)

    return {
        "job": job_service.serialize_job_detail(job_out),
        "listing": listing_out,
        "public_path": listing_out["public_path"],
        "public_url": listing_out["public_url"],
        "contractor_public_url": privacy.absolute_directory_url(
            privacy.contractor_path(
                await ensure_contractor_profile(db, company),
                company,
            )
        ),
    }


async def _publish_directory_for_job(
    db: AsyncSession,
    *,
    job: Job,
    company: Company,
) -> DirectoryListing:
    variant = _approved_directory_variant(job)
    profile = await ensure_contractor_profile(db, company, auto_publish=True)
    profile.published = True

    public_title = _public_title_from_variant(variant, job)
    public_summary = effective_body(variant)
    if not public_summary.strip():
        public_summary = public_title

    # Privacy: never use the private job title on the public page
    private_title = (job.title or "").strip()
    if private_title and private_title in public_title:
        parts: list[str] = []
        if job.service_key:
            parts.append(job.service_key.replace("_", " ").title())
        if job.city:
            parts.append(f"in {job.city}")
        public_title = (" ".join(parts) if parts else "Completed project")[:300]

    slug = _project_slug(job)
    seo_title, seo_description = _seo_for_listing(
        public_title, public_summary, job.city, job.service_key
    )

    listing = job.directory_listing
    now = datetime.now(timezone.utc)

    if listing is None:
        listing = DirectoryListing(
            job_id=job.id,
            company_id=company.id,
            contractor_profile_id=profile.id,
            slug=slug,
            public_title=public_title,
            public_summary=public_summary,
            service_key=job.service_key,
            location_display=job.location_display,
            city=job.city,
            state=job.state,
            postal_code=None,  # coarse public — omit precise postal from listing when possible
            status=DirectoryListingStatus.published,
            published_at=now,
            unpublished_at=None,
            seo_title=seo_title,
            seo_description=seo_description,
        )
        db.add(listing)
        await db.flush()
        job.directory_listing = listing
    else:
        listing.contractor_profile_id = profile.id
        listing.public_title = public_title
        listing.public_summary = public_summary
        listing.service_key = job.service_key
        listing.location_display = job.location_display
        listing.city = job.city
        listing.state = job.state
        # keep stable slug
        listing.status = DirectoryListingStatus.published
        listing.published_at = listing.published_at or now
        listing.unpublished_at = None
        listing.seo_title = seo_title
        listing.seo_description = seo_description
        await db.flush()

    image_urls = await _sync_listing_media(db, listing, job)
    listing.structured_data_json = _structured_data(
        public_title,
        public_summary,
        job.city,
        job.state,
        company.name,
        image_urls,
    )
    await db.flush()
    return listing


async def publish_listing(
    db: AsyncSession,
    company_id: UUID,
    listing_id: UUID,
    role: MembershipRole,
) -> dict:
    """Re-publish an existing listing (admin recovery). Re-validates job gate."""
    _ensure_can_publish(role)
    listing = await _get_company_listing(db, company_id, listing_id)
    job = await _load_job_for_publish(db, company_id, listing.job_id)
    counts = job_state.count_photos(job_service._ready_media(job))
    assert_job_publishable(job, list(job.content_variants or []), counts)

    company = await _load_company(db, company_id)
    await _publish_directory_for_job(db, job=job, company=company)

    now = datetime.now(timezone.utc)
    if job.status in {JobStatus.approved, JobStatus.published}:
        job.status = JobStatus.published
        job.published_at = job.published_at or now

    await db.commit()
    return await get_listing(db, company_id, listing_id)


async def unpublish_listing(
    db: AsyncSession,
    company_id: UUID,
    listing_id: UUID,
    role: MembershipRole,
) -> dict:
    _ensure_can_publish(role)
    listing = await _get_company_listing(db, company_id, listing_id)
    now = datetime.now(timezone.utc)
    before = {"status": listing.status.value}
    listing.status = DirectoryListingStatus.unpublished
    listing.unpublished_at = now
    await audit_service.record_event(
        db,
        company_id=company_id,
        entity_type="directory_listing",
        entity_id=listing.id,
        action="listing.unpublished",
        before=before,
        after={"status": listing.status.value, "job_id": str(listing.job_id)},
    )
    # Job stays published historically
    await db.commit()
    # Re-load with media to avoid async lazy-load on serialize
    return await get_listing(db, company_id, listing_id)


async def unpublish_for_job(
    db: AsyncSession,
    company_id: UUID,
    job_id: UUID,
    role: MembershipRole,
) -> dict:
    """Unpublish listing for a job if present."""
    _ensure_can_publish(role)
    result = await db.execute(
        select(DirectoryListing).where(
            DirectoryListing.job_id == job_id,
            DirectoryListing.company_id == company_id,
        )
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise not_found("LISTING_NOT_FOUND", "No directory listing for this job.")
    listing_id = listing.id
    return await unpublish_listing(db, company_id, listing_id, role)


# ---- Public API ----


async def public_list_contractors(
    db: AsyncSession,
    *,
    city: Optional[str] = None,
    state: Optional[str] = None,
    trade: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    q = (
        select(ContractorProfile)
        .join(Company, Company.id == ContractorProfile.company_id)
        .where(ContractorProfile.published.is_(True), Company.is_active.is_(True))
        .options(
            selectinload(ContractorProfile.company).selectinload(Company.services),
            selectinload(ContractorProfile.company).selectinload(Company.service_areas),
        )
        .order_by(ContractorProfile.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if trade:
        q = q.where(Company.trade.ilike(trade))
    result = await db.execute(q)
    profiles = list(result.scalars().all())

    out: list[dict] = []
    for profile in profiles:
        company = profile.company
        if city or state:
            # Filter by service areas or listings
            areas = company.service_areas or []
            match_area = any(
                (not city or (a.city and a.city.lower() == city.lower()))
                and (not state or (a.state and a.state.lower() == state.lower()))
                for a in areas
            )
            if not match_area and areas:
                # Also check published listings
                listings = await _published_listings_for_profile(db, profile.id, limit=1)
                match_listing = any(
                    (not city or (l.city and l.city.lower() == city.lower()))
                    and (not state or (l.state and l.state.lower() == state.lower()))
                    for l in listings
                )
                if not match_listing:
                    continue
            elif not match_area and not areas:
                continue
        projects = await _published_listings_for_profile(db, profile.id, limit=5)
        out.append(
            privacy.public_contractor_payload(
                profile,
                company,
                recent_projects=projects,
            )
        )
    return out


async def public_get_contractor(db: AsyncSession, slug: str) -> dict:
    result = await db.execute(
        select(ContractorProfile)
        .where(ContractorProfile.public_slug == slug, ContractorProfile.published.is_(True))
        .options(
            selectinload(ContractorProfile.company).selectinload(Company.services),
            selectinload(ContractorProfile.company).selectinload(Company.service_areas),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None or not profile.company or not profile.company.is_active:
        raise not_found("CONTRACTOR_NOT_FOUND", "Contractor not found.")
    projects = await _published_listings_for_profile(db, profile.id, limit=20)
    return privacy.public_contractor_payload(profile, profile.company, recent_projects=projects)


async def _published_listings_for_profile(
    db: AsyncSession, profile_id: UUID, *, limit: int = 20
) -> list[DirectoryListing]:
    result = await db.execute(
        select(DirectoryListing)
        .where(
            DirectoryListing.contractor_profile_id == profile_id,
            DirectoryListing.status == DirectoryListingStatus.published,
        )
        .options(
            selectinload(DirectoryListing.media_links).selectinload(DirectoryListingMedia.media_asset),
            selectinload(DirectoryListing.contractor_profile),
        )
        .order_by(DirectoryListing.published_at.desc().nullslast())
        .limit(limit)
    )
    return list(result.scalars().all())


async def public_list_projects(
    db: AsyncSession,
    *,
    city: Optional[str] = None,
    state: Optional[str] = None,
    service_key: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    # List endpoints skip media joins (summaries only) for performance.
    limit = min(max(limit, 1), 50)
    q = (
        select(DirectoryListing)
        .where(DirectoryListing.status == DirectoryListingStatus.published)
        .options(
            selectinload(DirectoryListing.contractor_profile).selectinload(ContractorProfile.company),
        )
        .order_by(DirectoryListing.published_at.desc().nullslast())
        .limit(limit)
        .offset(offset)
    )
    if city:
        q = q.where(DirectoryListing.city.ilike(city))
    if state:
        q = q.where(DirectoryListing.state.ilike(state))
    if service_key:
        q = q.where(DirectoryListing.service_key == service_key)
    result = await db.execute(q)
    listings = list(result.scalars().all())
    return [
        privacy.public_project_payload(
            l,
            include_media=False,
            contractor=l.contractor_profile,
            company=l.contractor_profile.company if l.contractor_profile else None,
        )
        for l in listings
    ]


async def public_get_project(db: AsyncSession, slug: str) -> dict:
    result = await db.execute(
        select(DirectoryListing)
        .where(
            DirectoryListing.slug == slug,
            DirectoryListing.status == DirectoryListingStatus.published,
        )
        .options(
            selectinload(DirectoryListing.media_links).selectinload(DirectoryListingMedia.media_asset),
            selectinload(DirectoryListing.contractor_profile).selectinload(ContractorProfile.company),
        )
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.")
    return privacy.public_project_payload(
        listing,
        contractor=listing.contractor_profile,
        company=listing.contractor_profile.company if listing.contractor_profile else None,
    )


async def create_lead_stub(
    db: AsyncSession,
    *,
    contractor_slug: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    message: Optional[str] = None,
    project_slug: Optional[str] = None,
) -> dict:
    """MVP lead form: validate contractor exists; log and return ack (no CRM)."""
    result = await db.execute(
        select(ContractorProfile).where(
            ContractorProfile.public_slug == contractor_slug,
            ContractorProfile.published.is_(True),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise not_found("CONTRACTOR_NOT_FOUND", "Contractor not found.")
    if not profile.lead_form_enabled:
        raise AppError(
            "LEADS_DISABLED",
            "This contractor is not accepting leads right now.",
            status_code=400,
        )
    logger.info(
        "directory_lead contractor=%s name=%s email=%s phone=%s project=%s message=%s",
        contractor_slug,
        name,
        email,
        phone,
        project_slug,
        (message or "")[:200],
    )
    return {
        "ok": True,
        "message": "Thanks — your message was received.",
        "contractor_slug": contractor_slug,
    }

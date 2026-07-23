"""Directory publishing service — first-party JobPulse (not social provider)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, func, or_, select
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
    DirectoryLead,
    DirectoryLeadStatus,
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
from app.modules.directory.catalog import (
    location_slug,
    parse_location_slug,
    service_description,
    service_display_name,
    service_key_from_slug,
    service_slug,
)
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


def _listing_query_options(*, with_media: bool = True):
    opts = [
        selectinload(DirectoryListing.contractor_profile).selectinload(ContractorProfile.company),
    ]
    if with_media:
        opts.append(
            selectinload(DirectoryListing.media_links).selectinload(DirectoryListingMedia.media_asset)
        )
    return opts


async def _published_listings_for_profile(
    db: AsyncSession, profile_id: UUID, *, limit: int = 20, offset: int = 0
) -> list[DirectoryListing]:
    result = await db.execute(
        select(DirectoryListing)
        .where(
            DirectoryListing.contractor_profile_id == profile_id,
            DirectoryListing.status == DirectoryListingStatus.published,
        )
        .options(*_listing_query_options(with_media=True))
        .order_by(DirectoryListing.published_at.desc().nullslast())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def _count_published_for_profile(db: AsyncSession, profile_id: UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(DirectoryListing)
        .where(
            DirectoryListing.contractor_profile_id == profile_id,
            DirectoryListing.status == DirectoryListingStatus.published,
        )
    )
    return int(result.scalar_one() or 0)


async def public_list_contractors(
    db: AsyncSession,
    *,
    city: Optional[str] = None,
    state: Optional[str] = None,
    trade: Optional[str] = None,
    service_key: Optional[str] = None,
    featured: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    limit = min(max(limit, 1), 50)
    q = (
        select(ContractorProfile)
        .join(Company, Company.id == ContractorProfile.company_id)
        .where(ContractorProfile.published.is_(True), Company.is_active.is_(True))
        .options(
            selectinload(ContractorProfile.company).selectinload(Company.services),
            selectinload(ContractorProfile.company).selectinload(Company.service_areas),
        )
        .order_by(
            ContractorProfile.featured.desc(),
            ContractorProfile.updated_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )
    if trade:
        q = q.where(Company.trade.ilike(trade))
    if featured is True:
        q = q.where(ContractorProfile.featured.is_(True))
    result = await db.execute(q)
    profiles = list(result.scalars().all())

    out: list[dict] = []
    for profile in profiles:
        company = profile.company
        if city or state:
            areas = company.service_areas or []
            match_area = any(
                (not city or (a.city and a.city.lower() == city.lower()))
                and (not state or (a.state and a.state.lower() == state.lower()))
                for a in areas
            )
            if not match_area:
                listings = await _published_listings_for_profile(db, profile.id, limit=5)
                match_listing = any(
                    (not city or (l.city and l.city.lower() == city.lower()))
                    and (not state or (l.state and l.state.lower() == state.lower()))
                    for l in listings
                )
                if not match_listing:
                    continue
        if service_key:
            projects_check = await _published_listings_for_profile(db, profile.id, limit=50)
            if not any(p.service_key == service_key for p in projects_check):
                # also company services
                if not any(s.service_key == service_key for s in (company.services or [])):
                    continue
            projects = [p for p in projects_check if p.service_key == service_key][:5]
            if not projects:
                projects = projects_check[:5]
        else:
            projects = await _published_listings_for_profile(db, profile.id, limit=5)
        count = await _count_published_for_profile(db, profile.id)
        out.append(
            privacy.public_contractor_payload(
                profile,
                company,
                recent_projects=projects,
                project_count=count,
            )
        )
    return out


async def public_get_contractor(
    db: AsyncSession,
    slug: str,
    *,
    project_limit: int = 50,
    project_offset: int = 0,
) -> dict:
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
    projects = await _published_listings_for_profile(
        db, profile.id, limit=project_limit, offset=project_offset
    )
    count = await _count_published_for_profile(db, profile.id)
    return privacy.public_contractor_payload(
        profile,
        profile.company,
        recent_projects=projects,
        project_count=count,
    )


async def public_list_projects(
    db: AsyncSession,
    *,
    q: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    service_key: Optional[str] = None,
    contractor_slug: Optional[str] = None,
    featured: Optional[bool] = None,
    has_before_after: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    limit = min(max(limit, 1), 50)
    query = (
        select(DirectoryListing)
        .where(DirectoryListing.status == DirectoryListingStatus.published)
        .options(*_listing_query_options(with_media=True))
        .order_by(
            DirectoryListing.featured.desc(),
            DirectoryListing.published_at.desc().nullslast(),
        )
        .limit(limit)
        .offset(offset)
    )
    if city:
        query = query.where(DirectoryListing.city.ilike(city))
    if state:
        query = query.where(DirectoryListing.state.ilike(state))
    if service_key:
        # Accept slug or raw key
        key = service_key_from_slug(service_key) if "-" in service_key else service_key
        query = query.where(
            or_(
                DirectoryListing.service_key == key,
                DirectoryListing.service_key == service_key,
            )
        )
    if featured is True:
        query = query.where(DirectoryListing.featured.is_(True))
    needs_profile_join = bool(contractor_slug or q)
    if needs_profile_join:
        query = query.join(
            ContractorProfile, ContractorProfile.id == DirectoryListing.contractor_profile_id
        ).outerjoin(Company, Company.id == ContractorProfile.company_id)
    if contractor_slug:
        query = query.where(ContractorProfile.public_slug == contractor_slug)
    if q:
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                DirectoryListing.public_title.ilike(term),
                DirectoryListing.public_summary.ilike(term),
                DirectoryListing.service_key.ilike(term),
                DirectoryListing.city.ilike(term),
                Company.name.ilike(term),
            )
        )
    result = await db.execute(query)
    listings = list(result.scalars().unique().all())
    cards: list[dict] = []
    for listing in listings:
        card = privacy.public_project_card(
            listing,
            company=listing.contractor_profile.company if listing.contractor_profile else None,
        )
        if has_before_after is True and not card.get("has_before_after"):
            continue
        cards.append(card)
    return cards


async def _related_projects(
    db: AsyncSession,
    listing: DirectoryListing,
    *,
    limit: int = 4,
) -> dict[str, list[dict]]:
    async def _fetch(**filters) -> list[dict]:
        items = await public_list_projects(db, limit=limit + 2, **filters)
        return [i for i in items if i["slug"] != listing.slug][:limit]

    same_contractor: list[dict] = []
    if listing.contractor_profile:
        same_contractor = await _fetch(contractor_slug=listing.contractor_profile.public_slug)
    same_city = await _fetch(city=listing.city) if listing.city else []
    same_service = await _fetch(service_key=listing.service_key) if listing.service_key else []
    nearby = await _fetch(state=listing.state) if listing.state else []
    return {
        "same_contractor": same_contractor,
        "same_city": same_city,
        "same_service": same_service,
        "nearby": nearby,
    }


async def public_get_project(db: AsyncSession, slug: str) -> dict:
    result = await db.execute(
        select(DirectoryListing)
        .where(
            DirectoryListing.slug == slug,
            DirectoryListing.status == DirectoryListingStatus.published,
        )
        .options(*_listing_query_options(with_media=True))
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise not_found("PROJECT_NOT_FOUND", "Project not found.")
    related = await _related_projects(db, listing)
    return privacy.public_project_payload(
        listing,
        contractor=listing.contractor_profile,
        company=listing.contractor_profile.company if listing.contractor_profile else None,
        related=related,
    )


async def public_list_services(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(
            DirectoryListing.service_key,
            func.count().label("project_count"),
        )
        .where(
            DirectoryListing.status == DirectoryListingStatus.published,
            DirectoryListing.service_key.is_not(None),
        )
        .group_by(DirectoryListing.service_key)
        .order_by(func.count().desc())
    )
    rows = result.all()
    out: list[dict] = []
    for service_key, count in rows:
        if not service_key:
            continue
        out.append(
            {
                "service_key": service_key,
                "slug": service_slug(service_key),
                "name": service_display_name(service_key),
                "description": service_description(service_key),
                "project_count": int(count),
                "public_path": f"/services/{service_slug(service_key)}",
            }
        )
    return out


async def public_get_service(db: AsyncSession, slug: str) -> dict:
    key = service_key_from_slug(slug)
    # Match either exact key or slugified form against inventory
    services = await public_list_services(db)
    match = next((s for s in services if s["slug"] == service_slug(slug) or s["service_key"] == key), None)
    if match is None:
        # Try loose match on slug
        match = next((s for s in services if s["slug"] == slug or service_slug(s["service_key"]) == slug), None)
    if match is None:
        raise not_found("SERVICE_NOT_FOUND", "No published projects for this service.")
    service_key = match["service_key"]
    projects = await public_list_projects(db, service_key=service_key, limit=24)
    contractors = await public_list_contractors(db, service_key=service_key, limit=12)
    # Locations for this service
    loc_result = await db.execute(
        select(
            DirectoryListing.city,
            DirectoryListing.state,
            func.count().label("project_count"),
        )
        .where(
            DirectoryListing.status == DirectoryListingStatus.published,
            DirectoryListing.service_key == service_key,
            DirectoryListing.city.is_not(None),
        )
        .group_by(DirectoryListing.city, DirectoryListing.state)
        .order_by(func.count().desc())
        .limit(20)
    )
    locations = [
        {
            "city": city,
            "state": state,
            "slug": location_slug(city, state),
            "project_count": int(count),
            "public_path": f"/locations/{location_slug(city, state)}/{service_slug(service_key)}",
        }
        for city, state, count in loc_result.all()
        if city
    ]
    return {
        **match,
        "projects": projects,
        "contractors": contractors,
        "locations": locations,
    }


async def public_list_locations(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(
            DirectoryListing.city,
            DirectoryListing.state,
            func.count().label("project_count"),
        )
        .where(
            DirectoryListing.status == DirectoryListingStatus.published,
            DirectoryListing.city.is_not(None),
        )
        .group_by(DirectoryListing.city, DirectoryListing.state)
        .order_by(func.count().desc())
    )
    out: list[dict] = []
    for city, state, count in result.all():
        if not city:
            continue
        slug = location_slug(city, state)
        out.append(
            {
                "city": city,
                "state": state,
                "slug": slug,
                "name": f"{city}{', ' + state if state else ''}",
                "project_count": int(count),
                "public_path": f"/locations/{slug}",
            }
        )
    return out


async def public_get_location(db: AsyncSession, slug: str) -> dict:
    city, state = parse_location_slug(slug)
    # Prefer exact inventory match on slug
    locations = await public_list_locations(db)
    match = next((loc for loc in locations if loc["slug"] == slug), None)
    if match is None and city:
        match = next(
            (
                loc
                for loc in locations
                if loc["city"]
                and loc["city"].lower() == city.lower()
                and (not state or (loc["state"] and loc["state"].lower() == state.lower()))
            ),
            None,
        )
    if match is None:
        raise not_found("LOCATION_NOT_FOUND", "No published projects in this location.")
    projects = await public_list_projects(
        db, city=match["city"], state=match.get("state"), limit=24
    )
    contractors = await public_list_contractors(
        db, city=match["city"], state=match.get("state"), limit=12
    )
    svc_result = await db.execute(
        select(DirectoryListing.service_key, func.count().label("project_count"))
        .where(
            DirectoryListing.status == DirectoryListingStatus.published,
            DirectoryListing.city.ilike(match["city"]),
            DirectoryListing.service_key.is_not(None),
        )
        .group_by(DirectoryListing.service_key)
        .order_by(func.count().desc())
    )
    services = [
        {
            "service_key": sk,
            "slug": service_slug(sk),
            "name": service_display_name(sk),
            "project_count": int(count),
            "public_path": f"/locations/{match['slug']}/{service_slug(sk)}",
        }
        for sk, count in svc_result.all()
        if sk
    ]
    return {
        **match,
        "projects": projects,
        "contractors": contractors,
        "services": services,
    }


async def public_get_location_service(db: AsyncSession, location_slug_value: str, service_slug_value: str) -> dict:
    loc = await public_get_location(db, location_slug_value)
    key = service_key_from_slug(service_slug_value)
    projects = await public_list_projects(
        db,
        city=loc["city"],
        state=loc.get("state"),
        service_key=key,
        limit=24,
    )
    if not projects:
        # try raw slug as service_key
        projects = await public_list_projects(
            db,
            city=loc["city"],
            state=loc.get("state"),
            service_key=service_slug_value,
            limit=24,
        )
    if not projects:
        raise not_found(
            "LOCATION_SERVICE_NOT_FOUND",
            "No published projects for this service in this location.",
        )
    contractors = await public_list_contractors(
        db, city=loc["city"], state=loc.get("state"), service_key=key, limit=12
    )
    resolved_key = projects[0].get("service_key") or key
    return {
        "location": {
            "city": loc["city"],
            "state": loc.get("state"),
            "slug": loc["slug"],
            "name": loc["name"],
            "public_path": loc["public_path"],
        },
        "service": {
            "service_key": resolved_key,
            "slug": service_slug(resolved_key),
            "name": service_display_name(resolved_key),
            "description": service_description(resolved_key),
            "public_path": f"/services/{service_slug(resolved_key)}",
        },
        "title": f"{service_display_name(resolved_key)} Projects in {loc['name']}",
        "project_count": len(projects),
        "projects": projects,
        "contractors": contractors,
        "public_path": f"/locations/{loc['slug']}/{service_slug(resolved_key)}",
    }


async def public_search(
    db: AsyncSession,
    *,
    q: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    service_key: Optional[str] = None,
    contractor_slug: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    projects = await public_list_projects(
        db,
        q=q,
        city=city,
        state=state,
        service_key=service_key,
        contractor_slug=contractor_slug,
        limit=limit,
        offset=offset,
    )
    contractors: list[dict] = []
    if q or city or state or service_key:
        contractors = await public_list_contractors(
            db,
            city=city,
            state=state,
            service_key=service_key,
            limit=min(limit, 10),
        )
        if q:
            term = q.strip().lower()
            contractors = [
                c
                for c in contractors
                if term in (c.get("company_name") or "").lower()
                or term in (c.get("headline") or "").lower()
                or term in (c.get("trade") or "").lower()
            ]
    return {
        "query": q,
        "projects": projects,
        "contractors": contractors,
        "limit": limit,
        "offset": offset,
    }


async def public_home(db: AsyncSession) -> dict:
    recent = await public_list_projects(db, limit=12)
    featured_projects = await public_list_projects(db, featured=True, limit=6)
    if not featured_projects:
        featured_projects = recent[:6]
    featured_contractors = await public_list_contractors(db, featured=True, limit=6)
    if not featured_contractors:
        featured_contractors = await public_list_contractors(db, limit=6)
    services = await public_list_services(db)
    locations = await public_list_locations(db)
    return {
        "recent_projects": recent,
        "featured_projects": featured_projects,
        "featured_contractors": featured_contractors,
        "popular_services": services[:8],
        "popular_locations": locations[:8],
    }


async def create_lead(
    db: AsyncSession,
    *,
    contractor_slug: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    message: Optional[str] = None,
    project_slug: Optional[str] = None,
    project_location: Optional[str] = None,
    service_requested: Optional[str] = None,
    preferred_contact_method: Optional[str] = None,
    source_page_type: Optional[str] = None,
    source_page_url: Optional[str] = None,
) -> dict:
    """Persist a homeowner lead with project/page attribution."""
    if not email and not phone:
        raise AppError(
            "CONTACT_REQUIRED",
            "Provide at least an email or phone number.",
            status_code=400,
        )
    result = await db.execute(
        select(ContractorProfile)
        .where(
            ContractorProfile.public_slug == contractor_slug,
            ContractorProfile.published.is_(True),
        )
        .options(selectinload(ContractorProfile.company))
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

    source_project_id = None
    if project_slug:
        listing_result = await db.execute(
            select(DirectoryListing).where(
                DirectoryListing.slug == project_slug,
                DirectoryListing.status == DirectoryListingStatus.published,
            )
        )
        listing = listing_result.scalar_one_or_none()
        if listing is not None:
            source_project_id = listing.id
            if not service_requested and listing.service_key:
                service_requested = listing.service_key
            if not project_location and listing.location_display:
                project_location = listing.location_display

    lead = DirectoryLead(
        contractor_profile_id=profile.id,
        company_id=profile.company_id,
        source_project_id=source_project_id,
        source_page_type=source_page_type,
        source_page_url=source_page_url,
        name=name.strip(),
        phone=phone,
        email=email,
        project_location=project_location,
        service_requested=service_requested,
        message=message,
        preferred_contact_method=preferred_contact_method,
        lead_status=DirectoryLeadStatus.new,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    logger.info(
        "directory_lead id=%s contractor=%s project=%s name=%s",
        lead.id,
        contractor_slug,
        project_slug,
        name,
    )
    return {
        "ok": True,
        "id": str(lead.id),
        "message": "Thanks — your message was received.",
        "contractor_slug": contractor_slug,
        "source_project_id": str(source_project_id) if source_project_id else None,
    }


# Backward-compatible alias
async def create_lead_stub(db: AsyncSession, **kwargs) -> dict:
    return await create_lead(db, **kwargs)

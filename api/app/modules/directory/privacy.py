"""Public serializers for the JobPulse directory.

Never expose private job title, customer PII, notes, transcripts, or storage keys.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core import storage as storage_svc
from app.core.config import get_settings
from app.core.slug import slugify
from app.db.models import (
    Company,
    ContractorProfile,
    DirectoryListing,
    DirectoryListingMedia,
    DirectoryListingStatus,
    MediaAsset,
)


def path_segment(value: Optional[str], fallback: str = "local") -> str:
    """Lowercase path-safe segment for public URLs."""
    if not value:
        return fallback
    return slugify(value) or fallback


def contractor_path(profile: ContractorProfile, company: Optional[Company] = None) -> str:
    state, city = _profile_location(profile, company)
    return f"/contractors/{path_segment(state, 'us')}/{path_segment(city, 'local')}/{profile.public_slug}"


def project_path(listing: DirectoryListing) -> str:
    return (
        f"/projects/{path_segment(listing.state, 'us')}"
        f"/{path_segment(listing.city, 'local')}"
        f"/{path_segment(listing.service_key, 'project')}"
        f"/{listing.slug}"
    )


def absolute_directory_url(path: str) -> str:
    base = get_settings().directory_url.rstrip("/")
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}"


def _profile_location(
    profile: ContractorProfile, company: Optional[Company] = None
) -> tuple[Optional[str], Optional[str]]:
    """Best-effort city/state for contractor URL paths.

    Avoids lazy-loading relationships in async context: only uses company
    service areas when already loaded / passed in.
    """
    company = company or None
    # Prefer company service areas (eager-loaded in public/admin paths)
    if company is not None:
        # Use __dict__ to avoid async lazy-load of service_areas
        areas = company.__dict__.get("service_areas")
        if areas:
            primary = next((a for a in areas if a.is_primary), None)
            area = primary or areas[0]
            if area is not None:
                return area.state, area.city
    # Fallback: already-loaded published listings on profile (sync-safe if present)
    listings = profile.__dict__.get("listings")
    if listings:
        for listing in listings:
            if listing.status == DirectoryListingStatus.published:
                if listing.state or listing.city:
                    return listing.state, listing.city
    return None, None


def public_media_item(link: DirectoryListingMedia, asset: Optional[MediaAsset] = None) -> dict[str, Any]:
    asset = asset or link.media_asset
    url = None
    if asset is not None and asset.processing_status.value != "pending_upload":
        try:
            url = storage_svc.public_or_signed_url(asset.storage_key)
        except Exception:  # noqa: BLE001 — best-effort URL
            url = None
    return {
        "id": str(link.id),
        "stage_label": link.stage_label,
        "display_order": link.display_order,
        "url": url,
        "mime_type": asset.mime_type if asset else None,
        "width": asset.width if asset else None,
        "height": asset.height if asset else None,
        # Explicitly omit storage_key, original_filename, metadata_json
    }


def public_project_payload(
    listing: DirectoryListing,
    *,
    include_media: bool = True,
    contractor: Optional[ContractorProfile] = None,
    company: Optional[Company] = None,
) -> dict[str, Any]:
    """Serialize a published project for public API consumers."""
    profile = contractor or listing.contractor_profile
    company = company or (profile.company if profile else None)

    media: list[dict[str, Any]] = []
    if include_media:
        for link in listing.media_links or []:
            media.append(public_media_item(link))

    contractor_slug = profile.public_slug if profile else None
    contractor_public_path = contractor_path(profile, company) if profile else None

    payload: dict[str, Any] = {
        "id": str(listing.id),
        "slug": listing.slug,
        "public_title": listing.public_title,
        "public_summary": listing.public_summary,
        "service_key": listing.service_key,
        "location_display": listing.location_display,
        "city": listing.city,
        "state": listing.state,
        "status": listing.status.value,
        "published_at": listing.published_at,
        "seo_title": listing.seo_title,
        "seo_description": listing.seo_description,
        "structured_data_json": listing.structured_data_json,
        "public_path": project_path(listing),
        "public_url": absolute_directory_url(project_path(listing)),
        "media": media,
        "contractor": {
            "slug": contractor_slug,
            "headline": profile.headline if profile else None,
            "company_name": company.name if company else None,
            "public_path": contractor_public_path,
            "public_url": (
                absolute_directory_url(contractor_public_path) if contractor_public_path else None
            ),
            "trade": company.trade if company else None,
        },
    }
    # Privacy guard: never attach private job fields as keys
    assert "job_title" not in payload
    assert "customer_name_private" not in payload
    return payload


def public_contractor_payload(
    profile: ContractorProfile,
    company: Company,
    *,
    recent_projects: Optional[list[DirectoryListing]] = None,
    services: Optional[list[Any]] = None,
    service_areas: Optional[list[Any]] = None,
) -> dict[str, Any]:
    projects = recent_projects or []
    project_summaries = [
        {
            "slug": p.slug,
            "public_title": p.public_title,
            "service_key": p.service_key,
            "city": p.city,
            "state": p.state,
            "location_display": p.location_display,
            "published_at": p.published_at,
            "public_path": project_path(p),
            "public_url": absolute_directory_url(project_path(p)),
        }
        for p in projects
        if p.status == DirectoryListingStatus.published
    ]

    svc_list = services if services is not None else list(getattr(company, "services", None) or [])
    area_list = (
        service_areas
        if service_areas is not None
        else list(getattr(company, "service_areas", None) or [])
    )

    path = contractor_path(profile, company)
    return {
        "id": str(profile.id),
        "slug": profile.public_slug,
        "headline": profile.headline,
        "public_description": profile.public_description,
        "company_name": company.name,
        "trade": company.trade,
        "contact_phone": profile.contact_phone,
        "website_url": profile.website_url,
        "lead_form_enabled": profile.lead_form_enabled,
        "seo_title": profile.seo_title,
        "seo_description": profile.seo_description,
        "public_path": path,
        "public_url": absolute_directory_url(path),
        "services": [
            {
                "service_key": s.service_key,
                "display_name": s.display_name,
            }
            for s in svc_list
            if getattr(s, "is_active", True)
        ],
        "service_areas": [
            {
                "city": a.city,
                "state": a.state,
                "display_name": a.display_name,
                "is_primary": a.is_primary,
            }
            for a in area_list
        ],
        "recent_projects": project_summaries,
    }


def admin_profile_payload(profile: ContractorProfile, company: Company) -> dict[str, Any]:
    path = contractor_path(profile, company)
    return {
        "id": profile.id,
        "company_id": profile.company_id,
        "public_slug": profile.public_slug,
        "headline": profile.headline,
        "public_description": profile.public_description,
        "contact_phone": profile.contact_phone,
        "contact_email": profile.contact_email,
        "website_url": profile.website_url,
        "lead_form_enabled": profile.lead_form_enabled,
        "published": profile.published,
        "seo_title": profile.seo_title,
        "seo_description": profile.seo_description,
        "public_path": path,
        "public_url": absolute_directory_url(path),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def admin_listing_payload(
    listing: DirectoryListing,
    *,
    include_media: bool = True,
) -> dict[str, Any]:
    media: list[dict[str, Any]] = []
    if include_media:
        for link in listing.media_links or []:
            item = public_media_item(link)
            item["media_asset_id"] = str(link.media_asset_id)
            media.append(item)

    path = project_path(listing)
    return {
        "id": listing.id,
        "job_id": listing.job_id,
        "company_id": listing.company_id,
        "contractor_profile_id": listing.contractor_profile_id,
        "slug": listing.slug,
        "public_title": listing.public_title,
        "public_summary": listing.public_summary,
        "service_key": listing.service_key,
        "location_display": listing.location_display,
        "city": listing.city,
        "state": listing.state,
        "postal_code": listing.postal_code,
        "status": listing.status.value,
        "published_at": listing.published_at,
        "unpublished_at": listing.unpublished_at,
        "seo_title": listing.seo_title,
        "seo_description": listing.seo_description,
        "structured_data_json": listing.structured_data_json,
        "public_path": path,
        "public_url": absolute_directory_url(path),
        "media": media,
        "created_at": listing.created_at,
        "updated_at": listing.updated_at,
    }


def assert_no_private_job_title(payload: dict[str, Any], private_title: str) -> None:
    """Test/runtime guard: private job title must not appear in public JSON."""
    import json

    blob = json.dumps(payload, default=str)
    if private_title and private_title in blob:
        raise ValueError("Private job title leaked into public payload.")

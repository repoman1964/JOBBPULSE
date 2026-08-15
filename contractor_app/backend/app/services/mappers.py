"""Map ORM entities to API response schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.company import Company, Contractor
from app.models.content import ContentPackage, GeneratedAsset, GeneratedAssetVersion
from app.models.job import Job
from app.models.media import MediaAsset
from app.models.social import SocialConnection
from app.schemas.common import (
    CompanyOut,
    ContentPackageOut,
    ContractorOut,
    GeneratedAssetOut,
    GeneratedAssetVersionOut,
    JobOut,
    MediaAssetOut,
    NotificationSettings,
    PhotoMaximums,
    PhotoMinimums,
    SocialConnectionOut,
)


def company_to_out(company: Company) -> CompanyOut:
    mins = company.photo_minimums_json or {}
    maxs = company.photo_maximums_json or {}
    notes = company.notification_settings_json or {}
    return CompanyOut(
        id=company.id,
        name=company.name,
        contactName=company.contact_name,
        phone=company.phone,
        email=company.email,
        website=company.website,
        serviceArea=company.service_area,
        photoMinimums=PhotoMinimums(
            before=int(mins.get("before", 2)),
            progress=int(mins.get("progress", 0)),
            after=int(mins.get("after", 2)),
        ),
        photoMaximums=PhotoMaximums(
            before=int(maxs.get("before", 15)),
            progress=int(maxs.get("progress", 30)),
            after=int(maxs.get("after", 15)),
        ),
        notificationSettings=NotificationSettings(
            contentReadyForApproval=bool(notes.get("contentReadyForApproval", True)),
            publishingComplete=bool(notes.get("publishingComplete", True)),
        ),
    )


def contractor_to_out(contractor: Contractor) -> ContractorOut:
    return ContractorOut(
        id=contractor.id,
        companyId=contractor.company_id,
        name=contractor.name,
        email=contractor.email,
        phone=contractor.phone,
        role=contractor.role,
    )


def job_to_out(
    job: Job,
    *,
    counts: dict[str, int],
    has_voice: bool,
    cover_url: str | None,
) -> JobOut:
    return JobOut(
        id=job.id,
        companyId=job.company_id,
        name=job.name,
        serviceType=job.service_type,
        city=job.city,
        region=job.region or "",
        locationText=job.location_text or "",
        internalNote=job.internal_note or "",
        assignedCrewMember=job.assigned_crew_member or "",
        publicStatus=job.public_status,
        coverUrl=cover_url,
        counts=counts,
        hasVoice=has_voice,
        createdAt=job.created_at,
        updatedAt=job.updated_at,
        submittedAt=job.submitted_at,
        approvedAt=job.approved_at,
        publishedAt=job.published_at,
    )


def media_to_out(
    media: MediaAsset,
    *,
    url: str,
    thumbnail_url: str | None = None,
) -> MediaAssetOut:
    return MediaAssetOut(
        id=media.id,
        jobId=media.job_id,
        kind=media.kind,
        photoCategory=media.photo_category,
        url=url,
        thumbnailUrl=thumbnail_url or url,
        mimeType=media.mime_type,
        byteSize=media.byte_size,
        durationMs=media.duration_ms,
        uploadStatus=media.upload_status,
        isFavorite=media.is_favorite,
        isDeleted=media.is_deleted,
        version=media.version,
        createdAt=media.created_at,
    )


def version_to_out(version: GeneratedAssetVersion) -> GeneratedAssetVersionOut:
    raw_ids = version.source_media_ids_json or []
    ids: list[UUID] = []
    for item in raw_ids:
        try:
            ids.append(UUID(str(item)))
        except (ValueError, TypeError):
            continue
    return GeneratedAssetVersionOut(
        id=version.id,
        version=version.version,
        title=version.title,
        body=version.body,
        preview=version.preview_json or {},
        sourceMediaIds=ids,
        createdAt=version.created_at,
    )


def asset_to_out(asset: GeneratedAsset) -> GeneratedAssetOut:
    versions = sorted(asset.versions, key=lambda v: v.version)
    active_id = asset.active_version_id
    if active_id is None and versions:
        active_id = versions[-1].id
    if active_id is None:
        # Should not happen for ready packages; use nil UUID for type safety
        active_id = asset.id
    return GeneratedAssetOut(
        id=asset.id,
        packageId=asset.package_id,
        destinationType=asset.destination_type,
        title=asset.title,
        body=asset.body,
        status=asset.status,
        activeVersionId=active_id,
        versions=[version_to_out(v) for v in versions],
        preview=asset.preview_json or {},
    )


def package_to_out(package: ContentPackage) -> ContentPackageOut:
    assets = sorted(package.assets, key=lambda a: a.destination_type)
    return ContentPackageOut(
        id=package.id,
        jobId=package.job_id,
        version=package.version,
        status=package.status,
        projectDescription=package.project_description,
        featuredBeforeMediaId=package.featured_before_media_id,
        featuredAfterMediaId=package.featured_after_media_id,
        assets=[asset_to_out(a) for a in assets],
    )


def social_to_out(conn: SocialConnection) -> SocialConnectionOut:
    return SocialConnectionOut(
        platform=conn.platform,
        status=conn.status,
        accountName=conn.provider_account_name,
        reason=conn.reason,
    )


def counts_from_media(media_list: list[MediaAsset]) -> dict[str, int]:
    counts: dict[str, int] = {"before": 0, "progress": 0, "after": 0}
    for m in media_list:
        if m.kind != "photo" or m.is_deleted or m.upload_status != "complete":
            continue
        if m.photo_category in counts:
            counts[m.photo_category] += 1
    return counts


def has_complete_voice(media_list: list[MediaAsset]) -> bool:
    return any(
        m.kind == "audio"
        and not m.is_deleted
        and m.upload_status == "complete"
        and m.is_active_voice
        for m in media_list
    )


def meets_minimums(counts: dict[str, int], minimums: dict[str, Any]) -> bool:
    return (
        counts.get("before", 0) >= int(minimums.get("before", 2))
        and counts.get("progress", 0) >= int(minimums.get("progress", 0))
        and counts.get("after", 0) >= int(minimums.get("after", 2))
    )

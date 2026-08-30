"""Public demo project payloads for the Red Clay conversion site."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import AppError
from app.core.slug import public_project_slug
from app.integrations.storage.s3 import ObjectStorage
from app.models.company import Contractor
from app.models.content import ContentPackage, GeneratedAsset
from app.models.job import Job
from app.models.media import MediaAsset
from app.schemas.common import APIModel

ELIGIBLE_PUBLIC_STATUSES = {
    "ready_for_approval",
    "publishing",
    "published",
    "publish_issue",
}

SOCIAL_DESTINATIONS = ("facebook", "facebook_group", "instagram", "google_business")


class DemoProjectListItem(APIModel):
    slug: str
    public_title: str = Field(alias="publicTitle")
    public_summary: str = Field(alias="publicSummary")
    service_type: str = Field(alias="serviceType")
    city: str
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    primary_image_url: str | None = Field(default=None, alias="primaryImageUrl")
    has_before: bool = Field(alias="hasBefore")
    has_after: bool = Field(alias="hasAfter")


class DemoMediaItem(APIModel):
    stage_label: str = Field(alias="stageLabel")
    url: str | None = None


class DemoSocialPost(APIModel):
    destination: str
    title: str
    body: str
    image_url: str | None = Field(default=None, alias="imageUrl")
    group_name: str | None = Field(default=None, alias="groupName")


class DemoProjectDetail(DemoProjectListItem):
    media: list[DemoMediaItem]
    social_posts: list[DemoSocialPost] = Field(alias="socialPosts")


def _asset_copy(asset: GeneratedAsset | Any) -> tuple[str, str]:
    active_id = getattr(asset, "active_version_id", None)
    versions = getattr(asset, "versions", None) or []
    if active_id:
        for version in versions:
            if version.id == active_id:
                return version.title, version.body
    return asset.title, asset.body


def _public_title_summary(
    job: Job, package: ContentPackage | None, assets: list[GeneratedAsset]
) -> tuple[str, str]:
    conv = next((a for a in assets if a.destination_type == "conversion_site"), None)
    fallback_title = f"{job.service_type} in {job.city}"
    fallback_summary = package.project_description if package else ""
    if conv is None:
        return fallback_title, fallback_summary
    title, body = _asset_copy(conv)
    return (title or fallback_title, body or fallback_summary)


def serialize_demo_list_item(
    job: Job | Any,
    package: ContentPackage | Any | None,
    assets: list[Any],
    *,
    primary_image_url: str | None,
    has_before: bool,
    has_after: bool,
) -> DemoProjectListItem:
    title, summary = _public_title_summary(job, package, assets)
    return DemoProjectListItem(
        slug=public_project_slug(title, job.id),
        publicTitle=title,
        publicSummary=summary,
        serviceType=job.service_type,
        city=job.city,
        publishedAt=job.published_at,
        primaryImageUrl=primary_image_url,
        hasBefore=has_before,
        hasAfter=has_after,
    )


def _signed_url(storage: ObjectStorage, media: MediaAsset | None) -> str | None:
    if media is None:
        return None
    key = media.preview_object_key or media.original_object_key or media.thumbnail_object_key
    if not key:
        return None
    try:
        return storage.presign_get(key)
    except Exception:
        return None


def _photo_by_category(media: list[MediaAsset], category: str) -> MediaAsset | None:
    for item in media:
        if (
            item.kind == "photo"
            and not item.is_deleted
            and item.upload_status == "complete"
            and item.photo_category == category
        ):
            return item
    return None


async def _contractor_for_email(db: AsyncSession, email: str) -> Contractor | None:
    result = await db.execute(
        select(Contractor)
        .where(Contractor.email == email)
        .order_by(Contractor.created_at.desc())
    )
    return result.scalars().first()


async def _latest_package(db: AsyncSession, job: Job) -> ContentPackage | None:
    result = await db.execute(
        select(ContentPackage)
        .where(ContentPackage.job_id == job.id)
        .options(
            selectinload(ContentPackage.assets).selectinload(GeneratedAsset.versions),
        )
        .order_by(ContentPackage.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _job_photos(db: AsyncSession, job: Job) -> list[MediaAsset]:
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.job_id == job.id,
            MediaAsset.company_id == job.company_id,
        )
    )
    return list(result.scalars().all())


def require_email(email: str | None) -> str:
    value = (email or "").strip().lower()
    if "@" not in value or "." not in value.split("@")[-1] or " " in value:
        raise AppError(
            "validation_error",
            "Please check the highlighted fields and try again.",
            status_code=422,
            field_errors={"email": "Enter a valid email."},
        )
    return value


async def list_demo_projects(
    db: AsyncSession,
    email: str,
    storage: ObjectStorage,
) -> list[DemoProjectListItem]:
    contractor = await _contractor_for_email(db, email)
    if contractor is None:
        return []
    result = await db.execute(
        select(Job).where(
            Job.company_id == contractor.company_id,
            Job.deleted_at.is_(None),
            Job.public_status.in_(ELIGIBLE_PUBLIC_STATUSES),
        ).order_by(Job.published_at.desc().nullslast(), Job.created_at.desc())
    )
    items: list[DemoProjectListItem] = []
    for job in result.scalars().all():
        package = await _latest_package(db, job)
        assets = list(package.assets) if package else []
        photos = await _job_photos(db, job)
        before = None
        after = None
        if package and package.featured_before_media_id:
            before = next((p for p in photos if p.id == package.featured_before_media_id), None)
        if package and package.featured_after_media_id:
            after = next((p for p in photos if p.id == package.featured_after_media_id), None)
        if before is None:
            before = _photo_by_category(photos, "before")
        if after is None:
            after = _photo_by_category(photos, "after")
        items.append(
            serialize_demo_list_item(
                job,
                package,
                assets,
                primary_image_url=_signed_url(storage, after),
                has_before=before is not None,
                has_after=after is not None,
            )
        )
    return items


async def get_demo_project(
    db: AsyncSession,
    slug: str,
    email: str,
    storage: ObjectStorage,
) -> DemoProjectDetail:
    contractor = await _contractor_for_email(db, email)
    if contractor is None:
        raise AppError("not_found", "Project not found.", status_code=404)
    result = await db.execute(
        select(Job).where(
            Job.company_id == contractor.company_id,
            Job.deleted_at.is_(None),
            Job.public_status.in_(ELIGIBLE_PUBLIC_STATUSES),
        )
    )
    for job in result.scalars().all():
        package = await _latest_package(db, job)
        assets = list(package.assets) if package else []
        title, summary = _public_title_summary(job, package, assets)
        if public_project_slug(title, job.id) != slug:
            continue
        photos = await _job_photos(db, job)
        before = None
        after = None
        if package and package.featured_before_media_id:
            before = next((p for p in photos if p.id == package.featured_before_media_id), None)
        if package and package.featured_after_media_id:
            after = next((p for p in photos if p.id == package.featured_after_media_id), None)
        if before is None:
            before = _photo_by_category(photos, "before")
        if after is None:
            after = _photo_by_category(photos, "after")
        after_url = _signed_url(storage, after)
        media: list[DemoMediaItem] = []
        if before is not None:
            media.append(DemoMediaItem(stageLabel="before", url=_signed_url(storage, before)))
        if after is not None:
            media.append(DemoMediaItem(stageLabel="after", url=after_url))
        social_posts: list[DemoSocialPost] = []
        by_dest = {a.destination_type: a for a in assets}
        for dest in SOCIAL_DESTINATIONS:
            asset = by_dest.get(dest)
            if asset is None and dest != "facebook_group":
                continue
            if asset is None:
                title_txt = "Neighborhood group"
                body_txt = (
                    f"Wrapped a {title.lower()} in {job.city} this week. "
                    "If a neighbor needs similar work, we walk the house and send a written number."
                )
            else:
                title_txt, body_txt = _asset_copy(asset)
            group_name = None
            if dest == "facebook_group":
                group_name = f"{job.city} Neighbors" if job.city else "Metro Atlanta Homeowners"
            social_posts.append(
                DemoSocialPost(
                    destination=dest,
                    title=title_txt,
                    body=body_txt,
                    imageUrl=after_url,
                    groupName=group_name,
                )
            )
        return DemoProjectDetail(
            slug=slug,
            publicTitle=title,
            publicSummary=summary,
            serviceType=job.service_type,
            city=job.city,
            publishedAt=job.published_at,
            primaryImageUrl=after_url,
            hasBefore=before is not None,
            hasAfter=after is not None,
            media=media,
            socialPosts=social_posts,
        )
    raise AppError("not_found", "Project not found.", status_code=404)

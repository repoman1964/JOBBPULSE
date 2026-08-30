"""Public demo project payloads for conversion sites (Red Clay)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core import storage as storage_svc
from app.core.exceptions import AppError
from app.core.slug import public_project_slug
from app.db.models import (
    CompanyMembership,
    ContentType,
    ContentVariant,
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipStatus,
    User,
)
from app.modules.content.service import effective_body
from app.modules.phone.status import to_public

ELIGIBLE_PUBLIC_STATUSES = {
    "ready_for_approval",
    "publishing",
    "published",
    "publish_issue",
}

ELIGIBLE_JOB_STATUSES = {
    JobStatus.awaiting_review,
    JobStatus.approved,
    JobStatus.publishing,
    JobStatus.published,
    JobStatus.publish_issue,
}

SOCIAL_DESTINATIONS = ("facebook", "facebook_group", "instagram", "google_business")


def require_email(email: str | None) -> str:
    value = (email or "").strip().lower()
    if "@" not in value or "." not in value.split("@")[-1] or " " in value:
        raise AppError(
            "VALIDATION_ERROR",
            "Please check the highlighted fields and try again.",
            status_code=422,
            details={"fieldErrors": {"email": "Enter a valid email."}},
        )
    return value


async def _company_id_for_email(db: AsyncSession, email: str) -> UUID | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    membership = (
        await db.execute(
            select(CompanyMembership)
            .where(
                CompanyMembership.user_id == user.id,
                CompanyMembership.status == MembershipStatus.active,
            )
            .order_by(CompanyMembership.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return membership.company_id if membership else None


def _signed_url(media: MediaAsset | None) -> str | None:
    if media is None or not media.storage_key:
        return None
    if media.processing_status == MediaProcessingStatus.pending_upload:
        return None
    try:
        return storage_svc.public_or_signed_url(media.storage_key)
    except Exception:
        return None


def _photo(media: list[MediaAsset], stage: MediaStageLabel, media_id: UUID | None = None) -> MediaAsset | None:
    ready = [
        m
        for m in media
        if m.asset_type == MediaAssetType.image
        and m.deleted_at is None
        and m.processing_status != MediaProcessingStatus.pending_upload
    ]
    if media_id:
        match = next((m for m in ready if m.id == media_id), None)
        if match:
            return match
    return next((m for m in ready if m.stage_label == stage), None)


def _variant_copy(variants: list[ContentVariant], *types: str) -> tuple[str, str]:
    for variant in variants:
        platform = (variant.platform_target or "").lower()
        ctype = variant.content_type.value if hasattr(variant.content_type, "value") else str(variant.content_type)
        if platform in types or ctype in types:
            title = variant.title or ""
            body = effective_body(variant)
            return title, body
    return "", ""


def _public_title_summary(job: Job, variants: list[ContentVariant]) -> tuple[str, str]:
    title, body = _variant_copy(
        variants,
        "directory_listing",
        "website_job_page",
        "conversion_site",
        ContentType.directory_listing.value,
    )
    fallback_title = f"{(job.service_key or 'project').replace('_', ' ')} in {job.city or 'metro Atlanta'}"
    fallback_summary = ""
    for variant in variants:
        if variant.content_type == ContentType.directory_listing:
            fallback_summary = effective_body(variant)
            break
    return title or fallback_title, body or fallback_summary


def serialize_demo_list_item(
    job: Job,
    variants: list[Any],
    *,
    primary_image_url: str | None,
    has_before: bool,
    has_after: bool,
) -> dict[str, Any]:
    title, summary = _public_title_summary(job, variants)
    return {
        "slug": public_project_slug(title, job.id),
        "publicTitle": title,
        "publicSummary": summary,
        "serviceType": job.service_key or "",
        "city": job.city or "",
        "publishedAt": job.published_at.isoformat() if job.published_at else None,
        "primaryImageUrl": primary_image_url,
        "hasBefore": has_before,
        "hasAfter": has_after,
    }


async def _jobs_for_company(db: AsyncSession, company_id: UUID) -> list[Job]:
    result = await db.execute(
        select(Job)
        .where(
            Job.company_id == company_id,
            Job.deleted_at.is_(None),
            Job.status.in_(ELIGIBLE_JOB_STATUSES),
        )
        .options(
            selectinload(Job.media_assets),
            selectinload(Job.content_variants),
        )
        .order_by(Job.published_at.desc().nullslast(), Job.created_at.desc())
    )
    return list(result.scalars().all())


async def list_demo_projects(db: AsyncSession, email: str) -> list[dict[str, Any]]:
    company_id = await _company_id_for_email(db, email)
    if company_id is None:
        return []
    items: list[dict[str, Any]] = []
    for job in await _jobs_for_company(db, company_id):
        if to_public(job.status) not in ELIGIBLE_PUBLIC_STATUSES:
            continue
        photos = list(job.media_assets or [])
        before = _photo(photos, MediaStageLabel.before, job.featured_before_media_id)
        after = _photo(photos, MediaStageLabel.after, job.featured_after_media_id)
        items.append(
            serialize_demo_list_item(
                job,
                list(job.content_variants or []),
                primary_image_url=_signed_url(after),
                has_before=before is not None,
                has_after=after is not None,
            )
        )
    return items


async def get_demo_project(db: AsyncSession, slug: str, email: str) -> dict[str, Any]:
    company_id = await _company_id_for_email(db, email)
    if company_id is None:
        raise AppError("NOT_FOUND", "Project not found.", status_code=404)
    for job in await _jobs_for_company(db, company_id):
        variants = list(job.content_variants or [])
        title, summary = _public_title_summary(job, variants)
        if public_project_slug(title, job.id) != slug:
            continue
        photos = list(job.media_assets or [])
        before = _photo(photos, MediaStageLabel.before, job.featured_before_media_id)
        after = _photo(photos, MediaStageLabel.after, job.featured_after_media_id)
        after_url = _signed_url(after)
        media = []
        if before is not None:
            media.append({"stageLabel": "before", "url": _signed_url(before)})
        if after is not None:
            media.append({"stageLabel": "after", "url": after_url})
        social_posts = []
        for dest in SOCIAL_DESTINATIONS:
            dest_title, dest_body = _variant_copy(variants, dest, dest.replace("_", ""))
            if not dest_title and dest != "facebook_group":
                if dest == "facebook":
                    dest_title, dest_body = _variant_copy(variants, "facebook", "primary_social")
                elif dest == "instagram":
                    dest_title, dest_body = _variant_copy(variants, "instagram", "short_caption")
                elif dest == "google_business":
                    dest_title, dest_body = _variant_copy(variants, "google_business")
            if not dest_title and dest != "facebook_group":
                continue
            if dest == "facebook_group" and not dest_title:
                dest_title = "Neighborhood group"
                dest_body = (
                    f"Wrapped a {title.lower()} in {job.city or 'the area'} this week. "
                    "If a neighbor needs similar work, we walk the house and send a written number."
                )
            group_name = None
            if dest == "facebook_group":
                group_name = f"{job.city} Neighbors" if job.city else "Metro Atlanta Homeowners"
            social_posts.append(
                {
                    "destination": dest,
                    "title": dest_title or title,
                    "body": dest_body or summary,
                    "imageUrl": after_url,
                    "groupName": group_name,
                }
            )
        return {
            **serialize_demo_list_item(
                job,
                variants,
                primary_image_url=after_url,
                has_before=before is not None,
                has_after=after is not None,
            ),
            "slug": slug,
            "media": media,
            "socialPosts": social_posts,
        }
    raise AppError("NOT_FOUND", "Project not found.", status_code=404)

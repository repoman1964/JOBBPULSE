"""Directory moderation: flag (company) + remove/list (platform admin)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.exceptions import AppError, forbidden, not_found
from app.core.permissions import can_approve_and_publish
from app.db.models import (
    DirectoryListing,
    DirectoryListingMedia,
    DirectoryListingStatus,
    MembershipRole,
    User,
)
from app.modules.audit import service as audit_service
from app.modules.directory import privacy as directory_privacy


def is_platform_admin(user: User) -> bool:
    emails = get_settings().founder_admin_email_set
    if not emails:
        return False
    return (user.email or "").strip().lower() in emails


def require_platform_admin(user: User) -> None:
    if not is_platform_admin(user):
        raise forbidden("Platform admin access required.")


async def _get_listing(db: AsyncSession, listing_id: UUID) -> DirectoryListing:
    result = await db.execute(
        select(DirectoryListing)
        .where(DirectoryListing.id == listing_id)
        .options(
            selectinload(DirectoryListing.media_links).selectinload(DirectoryListingMedia.media_asset),
            selectinload(DirectoryListing.contractor_profile),
        )
    )
    listing = result.scalar_one_or_none()
    if listing is None:
        raise not_found("LISTING_NOT_FOUND", "Directory listing not found.")
    return listing


async def flag_listing(
    db: AsyncSession,
    *,
    listing_id: UUID,
    user: User,
    company_id: UUID,
    role: MembershipRole,
    reason: Optional[str] = None,
) -> dict[str, Any]:
    """Manager+ of owning company OR platform admin can flag."""
    listing = await _get_listing(db, listing_id)
    is_owner_company = listing.company_id == company_id and can_approve_and_publish(role)
    if not is_owner_company and not is_platform_admin(user):
        raise forbidden("You do not have permission to flag this listing.")

    before = {"status": listing.status.value}
    listing.status = DirectoryListingStatus.flagged
    listing.unpublished_at = listing.unpublished_at or datetime.now(timezone.utc)

    await audit_service.record_event(
        db,
        company_id=listing.company_id,
        user_id=user.id,
        entity_type="directory_listing",
        entity_id=listing.id,
        action="listing.flagged",
        before=before,
        after={"status": listing.status.value, "reason": reason},
    )
    await db.commit()
    # Reload after commit — avoid async lazy-load / MissingGreenlet on expired attrs
    listing = await _get_listing(db, listing_id)
    return directory_privacy.admin_listing_payload(listing, include_media=False)


async def remove_listing(
    db: AsyncSession,
    *,
    listing_id: UUID,
    user: User,
    reason: Optional[str] = None,
) -> dict[str, Any]:
    require_platform_admin(user)
    listing = await _get_listing(db, listing_id)
    before = {"status": listing.status.value}
    listing.status = DirectoryListingStatus.removed
    listing.unpublished_at = listing.unpublished_at or datetime.now(timezone.utc)

    await audit_service.record_event(
        db,
        company_id=listing.company_id,
        user_id=user.id,
        entity_type="directory_listing",
        entity_id=listing.id,
        action="listing.removed",
        before=before,
        after={"status": listing.status.value, "reason": reason},
    )
    await db.commit()
    listing = await _get_listing(db, listing_id)
    return directory_privacy.admin_listing_payload(listing, include_media=False)


async def list_listings_admin(
    db: AsyncSession,
    *,
    user: User,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    require_platform_admin(user)
    stmt = (
        select(DirectoryListing)
        .options(selectinload(DirectoryListing.contractor_profile))
        .order_by(DirectoryListing.updated_at.desc())
        .limit(min(max(limit, 1), 100))
        .offset(max(offset, 0))
    )
    if status:
        try:
            status_enum = DirectoryListingStatus(status)
        except ValueError as exc:
            raise AppError(
                "INVALID_STATUS",
                f"Unknown listing status: {status}",
                status_code=400,
            ) from exc
        stmt = stmt.where(DirectoryListing.status == status_enum)

    result = await db.execute(stmt)
    return [
        directory_privacy.admin_listing_payload(l, include_media=False)
        for l in result.scalars().all()
    ]

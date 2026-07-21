"""Create and manage in-app notifications (email channel is stub-logged)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import not_found
from app.db.models import (
    CompanyMembership,
    MembershipRole,
    MembershipStatus,
    Notification,
    NotificationChannel,
    NotificationStatus,
)

logger = logging.getLogger("jobpulse.notifications")


def serialize_notification(n: Notification) -> dict[str, Any]:
    return {
        "id": n.id,
        "user_id": n.user_id,
        "company_id": n.company_id,
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "channel": n.channel.value,
        "status": n.status.value,
        "read_at": n.read_at,
        "sent_at": n.sent_at,
        "metadata_json": n.metadata_json,
        "created_at": n.created_at,
    }


async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID,
    company_id: UUID,
    type: str,
    title: str,
    body: str,
    metadata: Optional[dict[str, Any]] = None,
    channel: NotificationChannel = NotificationChannel.in_app,
) -> Notification:
    """Write an in-app notification. Email is stub-logged only."""
    now = datetime.now(timezone.utc)
    n = Notification(
        user_id=user_id,
        company_id=company_id,
        type=type,
        title=title[:300],
        body=body,
        channel=channel,
        status=NotificationStatus.sent if channel == NotificationChannel.in_app else NotificationStatus.pending,
        sent_at=now if channel == NotificationChannel.in_app else None,
        metadata_json=metadata,
    )
    db.add(n)
    await db.flush()

    if channel == NotificationChannel.email:
        # Stub delivery — never block product flows
        logger.info(
            "email_notification_stub type=%s user_id=%s company_id=%s title=%s",
            type,
            user_id,
            company_id,
            title,
        )
        n.status = NotificationStatus.sent
        n.sent_at = now
        await db.flush()

    return n


async def notify_company_managers(
    db: AsyncSession,
    *,
    company_id: UUID,
    type: str,
    title: str,
    body: str,
    metadata: Optional[dict[str, Any]] = None,
    extra_user_ids: Optional[list[UUID]] = None,
) -> list[Notification]:
    """Notify all active manager+ members, plus optional extra users (e.g. job creator)."""
    result = await db.execute(
        select(CompanyMembership.user_id).where(
            CompanyMembership.company_id == company_id,
            CompanyMembership.status == MembershipStatus.active,
            CompanyMembership.role.in_([MembershipRole.owner, MembershipRole.manager]),
        )
    )
    user_ids = {row[0] for row in result.all()}
    for uid in extra_user_ids or []:
        if uid:
            user_ids.add(uid)

    created: list[Notification] = []
    for uid in user_ids:
        n = await create_notification(
            db,
            user_id=uid,
            company_id=company_id,
            type=type,
            title=title,
            body=body,
            metadata=metadata,
        )
        created.append(n)
    return created


async def list_for_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    company_id: UUID,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    stmt = (
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.company_id == company_id,
        )
        .order_by(Notification.created_at.desc())
        .limit(min(max(limit, 1), 100))
        .offset(max(offset, 0))
    )
    if unread_only:
        stmt = stmt.where(Notification.status != NotificationStatus.read)

    result = await db.execute(stmt)
    items = [serialize_notification(n) for n in result.scalars().all()]

    count_stmt = select(Notification.id).where(
        Notification.user_id == user_id,
        Notification.company_id == company_id,
        Notification.status != NotificationStatus.read,
    )
    unread_result = await db.execute(count_stmt)
    unread_count = len(unread_result.all())
    return items, unread_count


async def mark_read(
    db: AsyncSession,
    *,
    user_id: UUID,
    company_id: UUID,
    notification_id: UUID,
) -> dict[str, Any]:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.company_id == company_id,
        )
    )
    n = result.scalar_one_or_none()
    if n is None:
        raise not_found("NOTIFICATION_NOT_FOUND", "Notification not found.")
    if n.status != NotificationStatus.read:
        n.status = NotificationStatus.read
        n.read_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(n)
    return serialize_notification(n)


async def mark_all_read(
    db: AsyncSession,
    *,
    user_id: UUID,
    company_id: UUID,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.company_id == company_id,
            Notification.status != NotificationStatus.read,
        )
        .values(status=NotificationStatus.read, read_at=now)
    )
    await db.commit()
    return {"ok": True}


# --- helpers for lifecycle events (generic safe copy, no private titles) ---


async def notify_generation_complete(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    requested_by: Optional[UUID],
    success: bool,
) -> None:
    if success:
        await notify_company_managers(
            db,
            company_id=company_id,
            type="generation.completed",
            title="Content ready to review",
            body="AI content is ready. Review and approve before publishing.",
            metadata={"job_id": str(job_id)},
            extra_user_ids=[requested_by] if requested_by else None,
        )
        await notify_company_managers(
            db,
            company_id=company_id,
            type="content.ready_for_review",
            title="Job awaiting review",
            body="A job has drafts waiting for your review.",
            metadata={"job_id": str(job_id)},
            extra_user_ids=[requested_by] if requested_by else None,
        )
    else:
        await notify_company_managers(
            db,
            company_id=company_id,
            type="generation.failed",
            title="Content generation failed",
            body="Generation failed. You can try again from the job screen.",
            metadata={"job_id": str(job_id)},
            extra_user_ids=[requested_by] if requested_by else None,
        )


async def notify_job_approved(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    user_id: Optional[UUID] = None,
) -> None:
    await notify_company_managers(
        db,
        company_id=company_id,
        type="job.approved",
        title="Job approved — ready to publish",
        body="Content was approved. Use Publish when you are ready.",
        metadata={"job_id": str(job_id)},
        extra_user_ids=[user_id] if user_id else None,
    )


async def notify_directory_published(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    listing_id: Optional[UUID] = None,
    public_path: Optional[str] = None,
) -> None:
    meta: dict[str, Any] = {"job_id": str(job_id)}
    if listing_id:
        meta["listing_id"] = str(listing_id)
    if public_path:
        meta["public_path"] = public_path
    await notify_company_managers(
        db,
        company_id=company_id,
        type="directory.published",
        title="Published to JobPulse directory",
        body="Your project is live on the public directory.",
        metadata=meta,
    )


async def notify_social_publication(
    db: AsyncSession,
    *,
    company_id: UUID,
    job_id: UUID,
    publication_id: UUID,
    platform: Optional[str],
    success: bool,
    error: Optional[str] = None,
) -> None:
    if success:
        await notify_company_managers(
            db,
            company_id=company_id,
            type="social.published",
            title="Social post published",
            body=f"Posted successfully{f' to {platform}' if platform else ''}.",
            metadata={
                "job_id": str(job_id),
                "publication_id": str(publication_id),
                "platform": platform,
            },
        )
    else:
        await notify_company_managers(
            db,
            company_id=company_id,
            type="social.failed",
            title="Social publish failed",
            body=error or "A social publication failed. You can retry from the job.",
            metadata={
                "job_id": str(job_id),
                "publication_id": str(publication_id),
                "platform": platform,
            },
        )

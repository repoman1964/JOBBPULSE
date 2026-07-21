"""Record and list company-scoped audit events."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import forbidden
from app.core.permissions import role_at_least
from app.db.models import AuditEvent, MembershipRole
from app.modules.audit.privacy import scrub_payload


async def record_event(
    db: AsyncSession,
    *,
    company_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    user_id: Optional[UUID] = None,
    before: Optional[dict[str, Any]] = None,
    after: Optional[dict[str, Any]] = None,
    private_title: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditEvent:
    """Append an audit row (caller owns the transaction commit)."""
    event = AuditEvent(
        company_id=company_id,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before_json=scrub_payload(before, private_title=private_title),
        after_json=scrub_payload(after, private_title=private_title),
        ip_address=(ip_address or None) and str(ip_address)[:64],
        user_agent=(user_agent or None) and str(user_agent)[:500],
    )
    db.add(event)
    await db.flush()
    return event


def serialize_event(event: AuditEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "company_id": event.company_id,
        "user_id": event.user_id,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "action": event.action,
        "before_json": event.before_json,
        "after_json": event.after_json,
        "ip_address": event.ip_address,
        "user_agent": event.user_agent,
        "created_at": event.created_at,
    }


async def list_events(
    db: AsyncSession,
    *,
    company_id: UUID,
    role: MembershipRole,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    if not role_at_least(role, MembershipRole.manager):
        raise forbidden("Only managers and owners can view audit events.")

    stmt = (
        select(AuditEvent)
        .where(AuditEvent.company_id == company_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(min(max(limit, 1), 100))
        .offset(max(offset, 0))
    )
    if entity_type:
        stmt = stmt.where(AuditEvent.entity_type == entity_type)
    if entity_id is not None:
        stmt = stmt.where(AuditEvent.entity_id == entity_id)
    if action:
        stmt = stmt.where(AuditEvent.action == action)

    result = await db.execute(stmt)
    return [serialize_event(e) for e in result.scalars().all()]

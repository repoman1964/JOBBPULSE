"""Soft billing gates and company billing status."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError, not_found
from app.db.models import Company

BLOCKED_STATUSES = frozenset({"canceled", "cancelled", "past_due", "unpaid"})


async def get_company(db: AsyncSession, company_id: UUID) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise not_found("COMPANY_NOT_FOUND", "Company not found.")
    return company


def company_can_publish(company: Company, *, enforce: Optional[bool] = None) -> bool:
    settings = get_settings()
    if enforce is None:
        enforce = settings.billing_enforce
    if not enforce:
        return True
    status = (company.subscription_status or "").strip().lower()
    return status not in BLOCKED_STATUSES


async def assert_company_can_publish(db: AsyncSession, company_id: UUID) -> Company:
    company = await get_company(db, company_id)
    if not company_can_publish(company):
        raise AppError(
            "BILLING_REQUIRED",
            "Publishing is blocked for this subscription status. Update billing to continue.",
            status_code=402,
            details={
                "subscription_status": company.subscription_status,
                "subscription_plan": company.subscription_plan,
            },
        )
    return company


def serialize_billing_status(company: Company) -> dict[str, Any]:
    settings = get_settings()
    return {
        "subscription_status": company.subscription_status,
        "subscription_plan": company.subscription_plan,
        "billing_customer_id": company.billing_customer_id,
        "trial_ends_at": company.trial_ends_at,
        "billing_enforce": settings.billing_enforce,
        "can_publish": company_can_publish(company),
    }


async def apply_stripe_event(
    db: AsyncSession,
    *,
    event_type: str,
    customer_id: Optional[str],
    subscription_status: Optional[str] = None,
    subscription_plan: Optional[str] = None,
    company_id: Optional[UUID] = None,
) -> dict[str, Any]:
    """Webhook stub: update company billing fields when we can resolve the company."""
    company: Optional[Company] = None
    if company_id:
        company = await get_company(db, company_id)
    elif customer_id:
        result = await db.execute(
            select(Company).where(Company.billing_customer_id == customer_id).limit(1)
        )
        company = result.scalar_one_or_none()

    if company is None:
        return {
            "ok": True,
            "matched": False,
            "event_type": event_type,
            "message": "No company matched; event logged only.",
        }

    if subscription_status:
        company.subscription_status = subscription_status[:40]
    if subscription_plan:
        company.subscription_plan = subscription_plan[:40]
    if customer_id and not company.billing_customer_id:
        company.billing_customer_id = customer_id[:200]

    await db.commit()
    await db.refresh(company)
    return {
        "ok": True,
        "matched": True,
        "event_type": event_type,
        "company_id": str(company.id),
        "billing": serialize_billing_status(company),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }

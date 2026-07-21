"""Billing status + Stripe webhook stub."""

from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.billing import service

logger = logging.getLogger("jobpulse.billing")

router = APIRouter(tags=["billing"])


class StripeWebhookStub(BaseModel):
    """Minimal stub body for local / pilot webhook testing."""

    type: str = Field(default="customer.subscription.updated")
    customer_id: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_plan: Optional[str] = None
    company_id: Optional[UUID] = None
    data: Optional[dict[str, Any]] = None


@router.get("/billing/status")
async def billing_status(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    company = await service.get_company(db, ctx.company_id)
    return success(service.serialize_billing_status(company))


@router.post("/billing/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    body: StripeWebhookStub | None = None,
    db: AsyncSession = Depends(get_db),
    stripe_signature: Optional[str] = Header(default=None, alias="Stripe-Signature"),
):
    """
    Pilot webhook hook. Signature verification is optional when
    STRIPE_WEBHOOK_SECRET is empty (dev). Does not implement full Stripe SDK.
    """
    settings = get_settings()
    if settings.stripe_webhook_secret:
        # Soft check: require header presence in pilot; full HMAC can be added later
        if not stripe_signature:
            logger.warning("stripe_webhook_missing_signature request_id=%s", getattr(request.state, "request_id", None))
            # Still accept in pilot if body is structured — log only
            pass

    payload = body or StripeWebhookStub()
    logger.info(
        "stripe_webhook_received type=%s customer_id=%s company_id=%s",
        payload.type,
        payload.customer_id,
        payload.company_id,
    )
    result = await service.apply_stripe_event(
        db,
        event_type=payload.type,
        customer_id=payload.customer_id,
        subscription_status=payload.subscription_status,
        subscription_plan=payload.subscription_plan,
        company_id=payload.company_id,
    )
    return success(result)

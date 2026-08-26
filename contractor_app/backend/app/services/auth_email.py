"""Email verification tokens for contractor signup."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.core.errors import AppError
from app.core.security import hash_token
from app.integrations.email.resend import send_verification_email
from app.models.auth import AuthChallenge
from app.models.company import Contractor
from app.models.enums import ContractorStatus

VERIFY_TYPE = "email_verify"


def verification_url(settings: Settings, token: str) -> str:
    base = settings.public_api_base_url.rstrip("/")
    return f"{base}/api/v1/auth/verify-email?token={token}"


async def _consume_outstanding(
    db: AsyncSession, contractor_id: UUID, now: datetime
) -> None:
    result = await db.execute(
        select(AuthChallenge).where(
            AuthChallenge.contractor_id == contractor_id,
            AuthChallenge.identifier_type == VERIFY_TYPE,
            AuthChallenge.consumed_at.is_(None),
        )
    )
    for challenge in result.scalars():
        challenge.consumed_at = now


async def issue_verification(
    db: AsyncSession,
    *,
    contractor: Contractor,
    settings: Settings,
) -> str:
    now = datetime.now(UTC)
    await _consume_outstanding(db, contractor.id, now)
    raw = secrets.token_urlsafe(32)
    db.add(
        AuthChallenge(
            identifier=contractor.email,
            identifier_type=VERIFY_TYPE,
            code_hash=hash_token(raw),
            expires_at=now + timedelta(hours=settings.auth_verification_ttl_hours),
            contractor_id=contractor.id,
            max_attempts=1,
        )
    )
    await db.flush()
    return raw


async def send_signup_verification(
    db: AsyncSession,
    *,
    contractor: Contractor,
    settings: Settings,
) -> str:
    token = await issue_verification(db, contractor=contractor, settings=settings)
    url = verification_url(settings, token)
    # Persist the pending account + token before talking to Resend. If delivery
    # fails, the contractor can tap Resend instead of being rolled back.
    await db.commit()
    await send_verification_email(
        settings=settings, to_email=contractor.email, verify_url=url
    )
    return url


async def activate_email(db: AsyncSession, token: str) -> Contractor:
    token = token.strip()
    if not token:
        raise AppError(
            "invalid_token",
            "That confirmation link is not valid.",
            status_code=400,
        )

    now = datetime.now(UTC)
    result = await db.execute(
        select(AuthChallenge).where(
            AuthChallenge.identifier_type == VERIFY_TYPE,
            AuthChallenge.code_hash == hash_token(token),
        )
    )
    challenge = result.scalar_one_or_none()
    if challenge is None:
        raise AppError(
            "invalid_token",
            "That confirmation link is not valid.",
            status_code=400,
        )

    def _aware(dt: datetime) -> datetime:
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)

    if challenge.contractor_id is None:
        raise AppError(
            "invalid_token",
            "That confirmation link is not valid.",
            status_code=400,
        )

    contractor_result = await db.execute(
        select(Contractor)
        .where(Contractor.id == challenge.contractor_id)
        .options(selectinload(Contractor.company))
    )
    contractor = contractor_result.scalar_one_or_none()
    if contractor is None:
        raise AppError(
            "invalid_token",
            "That confirmation link is not valid.",
            status_code=400,
        )

    already_active = (
        contractor.email_verified_at is not None
        and contractor.status == ContractorStatus.active.value
    )
    if already_active:
        if challenge.consumed_at is None:
            challenge.consumed_at = now
        return contractor

    if challenge.consumed_at is not None:
        raise AppError(
            "token_used",
            "That confirmation link was already used. Sign in instead.",
            status_code=400,
        )
    if _aware(challenge.expires_at) < now:
        raise AppError(
            "token_expired",
            "That confirmation link expired. Request a new one.",
            status_code=400,
        )

    challenge.consumed_at = now
    contractor.email_verified_at = now
    contractor.status = ContractorStatus.active.value
    await db.flush()
    return contractor

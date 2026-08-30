"""Auth business logic."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.exceptions import AppError, conflict, unauthorized
from app.core.permissions import can_approve_and_publish, can_create_jobs, can_manage_team
from app.core.security import (
    create_access_token,
    create_email_verify_token,
    create_refresh_token,
    hash_password,
    safe_decode_token,
    verify_password,
)
from app.core.slug import unique_company_slug
from app.db.models import (
    Company,
    CompanyMembership,
    MembershipRole,
    MembershipStatus,
    User,
)
from app.modules.auth.schemas import LoginRequest, RegisterRequest


async def register_user(db: AsyncSession, data: RegisterRequest) -> tuple[User, Company, CompanyMembership]:
    email = data.email.lower().strip()
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise conflict("EMAIL_EXISTS", "An account with this email already exists.")

    user = User(
        email=email,
        full_name=data.full_name.strip(),
        phone=data.phone,
        password_hash=hash_password(data.password),
        is_verified=False,
        is_active=True,
    )
    company = Company(
        name=data.company_name.strip(),
        slug=unique_company_slug(data.company_name),
        trade=data.trade.strip() if data.trade else None,
        phone=data.phone,
    )
    membership = CompanyMembership(
        user=user,
        company=company,
        role=MembershipRole.owner,
        status=MembershipStatus.active,
    )
    company.contact_name = user.full_name
    company.email = user.email
    db.add_all([user, company, membership])
    await db.commit()
    await db.refresh(user)
    await db.refresh(company)
    await db.refresh(membership)
    return user, company, membership


def verification_url_for(user: User) -> str:
    settings = get_settings()
    token = create_email_verify_token(user.id)
    base = settings.frontend_url.rstrip("/")
    return f"{base}/verify-email?token={token}"


def issue_verify_token(user: User) -> str:
    return create_email_verify_token(user.id)


async def authenticate(db: AsyncSession, data: LoginRequest) -> tuple[User, Company | None, CompanyMembership | None]:
    email = data.email.lower().strip()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password_hash):
        raise unauthorized("Invalid email or password.")
    if not user.is_active:
        raise unauthorized("This account is disabled.")
    if not user.is_verified:
        raise AppError(
            "EMAIL_NOT_VERIFIED",
            "Confirm your email before signing in. Check your inbox for the link.",
            status_code=403,
        )

    user.last_login_at = datetime.now(timezone.utc)
    membership = await _primary_membership(db, user.id)
    company = membership.company if membership else None
    await db.commit()
    await db.refresh(user)
    return user, company, membership


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> tuple[User, Company | None, CompanyMembership | None]:
    payload = safe_decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh" or not payload.get("sub"):
        raise unauthorized("Invalid or expired refresh token.")

    try:
        user_id = UUID(payload["sub"])
    except (TypeError, ValueError):
        raise unauthorized("Invalid refresh token subject.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise unauthorized("User not found or inactive.")

    membership = await _primary_membership(db, user.id)
    company = membership.company if membership else None
    return user, company, membership


async def _primary_membership(db: AsyncSession, user_id: UUID) -> CompanyMembership | None:
    result = await db.execute(
        select(CompanyMembership)
        .where(
            CompanyMembership.user_id == user_id,
            CompanyMembership.status == MembershipStatus.active,
        )
        .options(selectinload(CompanyMembership.company))
        .order_by(CompanyMembership.created_at.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def verify_email_token(db: AsyncSession, token: str) -> User:
    payload = safe_decode_token(token)
    if not payload or payload.get("type") != "email_verify" or not payload.get("sub"):
        raise AppError("INVALID_TOKEN", "That verification link is invalid or expired.", status_code=400)
    try:
        user_id = UUID(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise AppError("INVALID_TOKEN", "That verification link is invalid.", status_code=400) from exc
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AppError("INVALID_TOKEN", "That verification link is invalid.", status_code=400)
    user.is_verified = True
    await db.commit()
    await db.refresh(user)
    return user


async def resend_verification(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower().strip()))
    user = result.scalar_one_or_none()
    if user is None or user.is_verified:
        return None
    return user


def issue_tokens(user: User, company: Company | None) -> tuple[str, str]:
    company_id = company.id if company else None
    return create_access_token(user.id, company_id), create_refresh_token(user.id)


def permissions_for_role(role: MembershipRole | None) -> dict:
    if role is None:
        return {
            "can_manage_team": False,
            "can_approve_and_publish": False,
            "can_create_jobs": False,
            "role": None,
        }
    return {
        "can_manage_team": can_manage_team(role),
        "can_approve_and_publish": can_approve_and_publish(role),
        "can_create_jobs": can_create_jobs(role),
        "role": role.value,
    }

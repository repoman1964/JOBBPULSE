"""Auth business logic."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import conflict, unauthorized
from app.core.permissions import can_approve_and_publish, can_create_jobs, can_manage_team
from app.core.security import (
    create_access_token,
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
    db.add_all([user, company, membership])
    await db.commit()
    await db.refresh(user)
    await db.refresh(company)
    await db.refresh(membership)
    return user, company, membership


async def authenticate(db: AsyncSession, data: LoginRequest) -> tuple[User, Company | None, CompanyMembership | None]:
    email = data.email.lower().strip()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password_hash):
        raise unauthorized("Invalid email or password.")
    if not user.is_active:
        raise unauthorized("This account is disabled.")

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

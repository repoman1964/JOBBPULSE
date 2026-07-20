"""FastAPI dependencies for auth and company context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import forbidden, unauthorized
from app.core.permissions import role_at_least
from app.core.security import safe_decode_token
from app.db.models import Company, CompanyMembership, MembershipRole, MembershipStatus, User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user: User
    membership: CompanyMembership
    company: Company

    @property
    def role(self) -> MembershipRole:
        return self.membership.role

    @property
    def user_id(self) -> UUID:
        return self.user.id

    @property
    def company_id(self) -> UUID:
        return self.company.id


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized()

    payload = safe_decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access" or not payload.get("sub"):
        raise unauthorized("Invalid or expired access token.")

    try:
        user_id = UUID(payload["sub"])
    except (TypeError, ValueError):
        raise unauthorized("Invalid token subject.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise unauthorized("User not found or inactive.")
    return user


async def get_auth_context(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    result = await db.execute(
        select(CompanyMembership)
        .where(
            CompanyMembership.user_id == user.id,
            CompanyMembership.status == MembershipStatus.active,
        )
        .options(selectinload(CompanyMembership.company))
        .order_by(CompanyMembership.created_at.asc())
        .limit(1)
    )
    membership = result.scalar_one_or_none()
    if membership is None or membership.company is None or not membership.company.is_active:
        raise forbidden("No active company membership found.")

    return AuthContext(user=user, membership=membership, company=membership.company)


def require_role(minimum: MembershipRole):
    async def _checker(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if not role_at_least(ctx.role, minimum):
            raise forbidden(f"Requires {minimum.value} role or higher.")
        return ctx

    return _checker

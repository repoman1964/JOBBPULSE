"""FastAPI dependencies: DB session, current user, settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.company import Company, Contractor

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    contractor: Contractor
    company: Company
    company_id: UUID
    contractor_id: UUID


async def get_settings_dep() -> Settings:
    return get_settings()


async def get_current_auth(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    token: str | None = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise AppError("unauthorized", "Please sign in to continue.", status_code=401)

    try:
        payload = decode_access_token(token, settings)
    except jwt.ExpiredSignatureError as exc:
        raise AppError(
            "session_expired",
            "Your session expired. Please sign in again.",
            status_code=401,
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError("unauthorized", "Invalid session token.", status_code=401) from exc

    if payload.get("type") != "access":
        raise AppError("unauthorized", "Invalid session token.", status_code=401)

    contractor_id = UUID(payload["sub"])
    company_id = UUID(payload["company_id"])

    result = await db.execute(
        select(Contractor)
        .where(Contractor.id == contractor_id, Contractor.company_id == company_id)
        .options(selectinload(Contractor.company))
    )
    contractor = result.scalar_one_or_none()
    if contractor is None or contractor.status != "active":
        raise AppError("unauthorized", "Account not found or inactive.", status_code=401)

    return AuthContext(
        contractor=contractor,
        company=contractor.company,
        company_id=company_id,
        contractor_id=contractor_id,
    )


async def get_optional_auth(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> AuthContext | None:
    if credentials is None:
        return None
    try:
        return await get_current_auth(db, settings, credentials)
    except AppError:
        return None


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentAuth = Annotated[AuthContext, Depends(get_current_auth)]
AppSettings = Annotated[Settings, Depends(get_settings_dep)]

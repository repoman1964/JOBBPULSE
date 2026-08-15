"""Company profile and settings."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentAuth, DbSession
from app.core.errors import AppError
from app.models.company import Company
from app.schemas.common import CompanyOut
from app.schemas.requests import UpdateCompanyRequest, UpdateNotificationSettingsRequest
from app.services.mappers import company_to_out

router = APIRouter(tags=["company"])


async def _load_company(db: DbSession, company_id) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise AppError("not_found", "Company not found.", status_code=404)
    return company


@router.get("/company", response_model=CompanyOut)
async def get_company(auth: CurrentAuth, db: DbSession) -> CompanyOut:
    company = await _load_company(db, auth.company_id)
    return company_to_out(company)


@router.patch("/company", response_model=CompanyOut)
async def update_company(
    body: UpdateCompanyRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> CompanyOut:
    company = await _load_company(db, auth.company_id)
    data = body.model_dump(by_alias=False, exclude_unset=True)
    field_map = {
        "name": "name",
        "contact_name": "contact_name",
        "phone": "phone",
        "email": "email",
        "website": "website",
        "service_area": "service_area",
    }
    for key, attr in field_map.items():
        if key in data and data[key] is not None:
            setattr(company, attr, data[key])
    await db.flush()
    return company_to_out(company)


@router.get("/company/settings", response_model=CompanyOut)
async def get_company_settings(auth: CurrentAuth, db: DbSession) -> CompanyOut:
    return await get_company(auth, db)


@router.patch("/company/settings", response_model=CompanyOut)
async def update_company_settings(
    body: UpdateNotificationSettingsRequest,
    auth: CurrentAuth,
    db: DbSession,
) -> CompanyOut:
    company = await _load_company(db, auth.company_id)
    notes = dict(company.notification_settings_json or {})
    data = body.model_dump(by_alias=True, exclude_unset=True)
    for key, value in data.items():
        if value is not None:
            notes[key] = value
    company.notification_settings_json = notes
    await db.flush()
    return company_to_out(company)


@router.get("/me", response_model=CompanyOut, include_in_schema=False)
async def me_company_compat() -> None:
    """Placeholder — actual /me is under auth router with SessionOut."""
    raise AppError("not_found", "Use GET /api/v1/auth/me or GET /api/v1/me", status_code=404)

"""Create a company and owner contractor for self-serve signup."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.slug import slugify
from app.models.company import Company, Contractor
from app.models.enums import ContractorRole, ContractorStatus


async def unique_company_slug(db: AsyncSession, company_name: str) -> str:
    base = slugify(company_name, max_length=80)
    existing = {
        row[0]
        for row in (await db.execute(select(Company.slug).where(Company.slug.like(f"{base}%")))).all()
    }
    if base not in existing:
        return base
    for i in range(2, 100):
        candidate = f"{base}-{i}"
        if candidate not in existing:
            return candidate
    return f"{base}-{uuid4().hex[:6]}"


async def register_owner(
    db: AsyncSession,
    *,
    name: str,
    email: str,
    company_name: str,
    phone: str = "",
) -> tuple[Company, Contractor]:
    normalized_email = email.strip().lower()
    result = await db.execute(select(Contractor).where(Contractor.email == normalized_email))
    if result.scalar_one_or_none() is not None:
        raise AppError(
            "email_taken",
            "An account with that email already exists. Sign in instead.",
            status_code=409,
        )

    company = Company(
        name=company_name.strip(),
        slug=await unique_company_slug(db, company_name),
        contact_name=name.strip(),
        phone=phone,
        email=normalized_email,
    )
    db.add(company)
    await db.flush()

    contractor = Contractor(
        company_id=company.id,
        name=name.strip(),
        email=normalized_email,
        phone=phone,
        role=ContractorRole.owner.value,
        status=ContractorStatus.active.value,
    )
    db.add(contractor)
    await db.flush()
    return company, contractor

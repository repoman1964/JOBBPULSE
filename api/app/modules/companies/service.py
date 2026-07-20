"""Company and team business logic."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import conflict, forbidden, not_found
from app.core.security import hash_password
from app.db.models import (
    Company,
    CompanyMembership,
    CompanyService,
    CompanyServiceArea,
    MembershipRole,
    MembershipStatus,
    User,
)
from app.modules.companies.schemas import (
    CompanyUpdate,
    MemberInvite,
    MemberUpdate,
    ServiceAreaCreate,
    ServiceCreate,
    ServiceUpdate,
)


async def get_company(db: AsyncSession, company_id: UUID) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise not_found("COMPANY_NOT_FOUND", "Company not found.")
    return company


async def update_company(db: AsyncSession, company: Company, data: CompanyUpdate) -> Company:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.commit()
    await db.refresh(company)
    return company


async def list_services(db: AsyncSession, company_id: UUID) -> list[CompanyService]:
    result = await db.execute(
        select(CompanyService)
        .where(CompanyService.company_id == company_id)
        .order_by(CompanyService.display_name.asc())
    )
    return list(result.scalars().all())


async def create_service(db: AsyncSession, company_id: UUID, data: ServiceCreate) -> CompanyService:
    service = CompanyService(
        company_id=company_id,
        service_key=data.service_key.strip().lower().replace(" ", "_"),
        display_name=data.display_name.strip(),
        description=data.description,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


async def update_service(
    db: AsyncSession, company_id: UUID, service_id: UUID, data: ServiceUpdate
) -> CompanyService:
    service = await _get_service(db, company_id, service_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    await db.commit()
    await db.refresh(service)
    return service


async def delete_service(db: AsyncSession, company_id: UUID, service_id: UUID) -> None:
    service = await _get_service(db, company_id, service_id)
    await db.delete(service)
    await db.commit()


async def list_service_areas(db: AsyncSession, company_id: UUID) -> list[CompanyServiceArea]:
    result = await db.execute(
        select(CompanyServiceArea)
        .where(CompanyServiceArea.company_id == company_id)
        .order_by(CompanyServiceArea.display_name.asc())
    )
    return list(result.scalars().all())


async def create_service_area(
    db: AsyncSession, company_id: UUID, data: ServiceAreaCreate
) -> CompanyServiceArea:
    area = CompanyServiceArea(
        company_id=company_id,
        country_code=data.country_code.upper(),
        state=data.state,
        metro_area=data.metro_area,
        city=data.city,
        postal_code=data.postal_code,
        display_name=data.display_name.strip(),
        is_primary=data.is_primary,
    )
    db.add(area)
    await db.commit()
    await db.refresh(area)
    return area


async def delete_service_area(db: AsyncSession, company_id: UUID, area_id: UUID) -> None:
    result = await db.execute(
        select(CompanyServiceArea).where(
            CompanyServiceArea.id == area_id,
            CompanyServiceArea.company_id == company_id,
        )
    )
    area = result.scalar_one_or_none()
    if area is None:
        raise not_found("SERVICE_AREA_NOT_FOUND", "Service area not found.")
    await db.delete(area)
    await db.commit()


async def list_members(db: AsyncSession, company_id: UUID) -> list[CompanyMembership]:
    result = await db.execute(
        select(CompanyMembership)
        .where(CompanyMembership.company_id == company_id)
        .options(selectinload(CompanyMembership.user))
        .order_by(CompanyMembership.created_at.asc())
    )
    return list(result.scalars().all())


async def invite_member(
    db: AsyncSession, company_id: UUID, data: MemberInvite
) -> CompanyMembership:
    email = data.email.lower().strip()
    role = MembershipRole(data.role)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email=email,
            full_name=data.full_name.strip(),
            password_hash=hash_password(data.password),
            is_verified=False,
            is_active=True,
        )
        db.add(user)
        await db.flush()
    else:
        existing = await db.execute(
            select(CompanyMembership).where(
                CompanyMembership.company_id == company_id,
                CompanyMembership.user_id == user.id,
            )
        )
        if existing.scalar_one_or_none():
            raise conflict("MEMBER_EXISTS", "This user is already a company member.")

    membership = CompanyMembership(
        company_id=company_id,
        user_id=user.id,
        role=role,
        status=MembershipStatus.active,
    )
    db.add(membership)
    await db.commit()
    result = await db.execute(
        select(CompanyMembership)
        .where(CompanyMembership.id == membership.id)
        .options(selectinload(CompanyMembership.user))
    )
    return result.scalar_one()


async def update_member(
    db: AsyncSession,
    company_id: UUID,
    membership_id: UUID,
    data: MemberUpdate,
    actor_user_id: UUID,
) -> CompanyMembership:
    membership = await _get_membership(db, company_id, membership_id)
    updates = data.model_dump(exclude_unset=True)

    if "role" in updates:
        new_role = MembershipRole(updates["role"])
        if membership.role == MembershipRole.owner and new_role != MembershipRole.owner:
            await _ensure_another_owner(db, company_id, membership.id)
        membership.role = new_role

    if "status" in updates:
        new_status = MembershipStatus(updates["status"])
        if (
            membership.role == MembershipRole.owner
            and membership.user_id == actor_user_id
            and new_status != MembershipStatus.active
        ):
            raise forbidden("Owners cannot disable their own membership.")
        if membership.role == MembershipRole.owner and new_status != MembershipStatus.active:
            await _ensure_another_owner(db, company_id, membership.id)
        membership.status = new_status

    await db.commit()
    result = await db.execute(
        select(CompanyMembership)
        .where(CompanyMembership.id == membership.id)
        .options(selectinload(CompanyMembership.user))
    )
    return result.scalar_one()


async def remove_member(
    db: AsyncSession, company_id: UUID, membership_id: UUID, actor_user_id: UUID
) -> None:
    membership = await _get_membership(db, company_id, membership_id)
    if membership.user_id == actor_user_id:
        raise forbidden("You cannot remove yourself.")
    if membership.role == MembershipRole.owner:
        await _ensure_another_owner(db, company_id, membership.id)
    await db.delete(membership)
    await db.commit()


async def _get_service(db: AsyncSession, company_id: UUID, service_id: UUID) -> CompanyService:
    result = await db.execute(
        select(CompanyService).where(
            CompanyService.id == service_id,
            CompanyService.company_id == company_id,
        )
    )
    service = result.scalar_one_or_none()
    if service is None:
        raise not_found("SERVICE_NOT_FOUND", "Service not found.")
    return service


async def _get_membership(
    db: AsyncSession, company_id: UUID, membership_id: UUID
) -> CompanyMembership:
    result = await db.execute(
        select(CompanyMembership)
        .where(
            CompanyMembership.id == membership_id,
            CompanyMembership.company_id == company_id,
        )
        .options(selectinload(CompanyMembership.user))
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise not_found("MEMBER_NOT_FOUND", "Membership not found.")
    return membership


async def _ensure_another_owner(db: AsyncSession, company_id: UUID, excluding_id: UUID) -> None:
    result = await db.execute(
        select(CompanyMembership).where(
            CompanyMembership.company_id == company_id,
            CompanyMembership.role == MembershipRole.owner,
            CompanyMembership.status == MembershipStatus.active,
            CompanyMembership.id != excluding_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise forbidden("Company must keep at least one active owner.")

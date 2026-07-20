"""Company and team HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context, require_role
from app.core.responses import success
from app.db.models import MembershipRole
from app.db.session import get_db
from app.modules.companies import service
from app.modules.companies.schemas import (
    CompanyOut,
    CompanyUpdate,
    MemberInvite,
    MemberOut,
    MemberUpdate,
    ServiceAreaCreate,
    ServiceAreaOut,
    ServiceCreate,
    ServiceOut,
    ServiceUpdate,
)

router = APIRouter(prefix="/company", tags=["company"])


def _member_out(m) -> dict:
    return MemberOut(
        id=m.id,
        user_id=m.user_id,
        email=m.user.email,
        full_name=m.user.full_name,
        role=m.role.value,
        status=m.status.value,
        created_at=m.created_at,
    ).model_dump(mode="json")


@router.get("")
async def get_company(ctx: AuthContext = Depends(get_auth_context)):
    return success(CompanyOut.model_validate(ctx.company).model_dump(mode="json"))


@router.patch("")
async def patch_company(
    body: CompanyUpdate,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    company = await service.update_company(db, ctx.company, body)
    return success(CompanyOut.model_validate(company).model_dump(mode="json"))


@router.get("/services")
async def get_services(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_services(db, ctx.company_id)
    return success([ServiceOut.model_validate(i).model_dump(mode="json") for i in items])


@router.post("/services", status_code=201)
async def post_service(
    body: ServiceCreate,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    item = await service.create_service(db, ctx.company_id, body)
    return success(ServiceOut.model_validate(item).model_dump(mode="json"))


@router.patch("/services/{service_id}")
async def patch_service(
    service_id: UUID,
    body: ServiceUpdate,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    item = await service.update_service(db, ctx.company_id, service_id, body)
    return success(ServiceOut.model_validate(item).model_dump(mode="json"))


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: UUID,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_service(db, ctx.company_id, service_id)
    return success({"deleted": True})


@router.get("/service-areas")
async def get_service_areas(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_service_areas(db, ctx.company_id)
    return success([ServiceAreaOut.model_validate(i).model_dump(mode="json") for i in items])


@router.post("/service-areas", status_code=201)
async def post_service_area(
    body: ServiceAreaCreate,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    item = await service.create_service_area(db, ctx.company_id, body)
    return success(ServiceAreaOut.model_validate(item).model_dump(mode="json"))


@router.delete("/service-areas/{area_id}")
async def delete_service_area(
    area_id: UUID,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_service_area(db, ctx.company_id, area_id)
    return success({"deleted": True})


@router.get("/members")
async def get_members(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_members(db, ctx.company_id)
    return success([_member_out(i) for i in items])


@router.post("/members/invite", status_code=201)
async def invite_member(
    body: MemberInvite,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    item = await service.invite_member(db, ctx.company_id, body)
    return success(_member_out(item))


@router.patch("/members/{membership_id}")
async def patch_member(
    membership_id: UUID,
    body: MemberUpdate,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    item = await service.update_member(db, ctx.company_id, membership_id, body, ctx.user_id)
    return success(_member_out(item))


@router.delete("/members/{membership_id}")
async def delete_member(
    membership_id: UUID,
    ctx: AuthContext = Depends(require_role(MembershipRole.owner)),
    db: AsyncSession = Depends(get_db),
):
    await service.remove_member(db, ctx.company_id, membership_id, ctx.user_id)
    return success({"deleted": True})

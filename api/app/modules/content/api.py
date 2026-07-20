"""Content review HTTP routes (spec §10.8)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.content import service
from app.modules.content.schemas import (
    ApprovalReadinessOut,
    ContentUpdate,
    ContentVariantDetailOut,
    RejectRequest,
)
from app.modules.jobs.schemas import JobDetailOut

router = APIRouter(tags=["content"])


def _variant_out(data: dict) -> dict:
    return ContentVariantDetailOut.model_validate(data).model_dump(mode="json")


@router.get("/content/{content_id}")
async def get_content(
    content_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.get_variant(db, ctx.company_id, content_id)
    return success(_variant_out(payload))


@router.patch("/content/{content_id}")
async def patch_content(
    content_id: UUID,
    body: ContentUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    fields_set = set(body.model_fields_set)
    payload = await service.update_variant(
        db,
        company_id=ctx.company_id,
        content_id=content_id,
        role=ctx.role,
        body_edited=body.body_edited,
        title=body.title,
        call_to_action=body.call_to_action,
        hashtags_json=body.hashtags_json,
        fields_set=fields_set,
    )
    return success(_variant_out(payload))


@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.approve_variant(
        db,
        company_id=ctx.company_id,
        content_id=content_id,
        user_id=ctx.user_id,
        role=ctx.role,
    )
    return success(_variant_out(payload))


@router.post("/content/{content_id}/reject")
async def reject_content(
    content_id: UUID,
    body: RejectRequest | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.reject_variant(
        db,
        company_id=ctx.company_id,
        content_id=content_id,
        user_id=ctx.user_id,
        role=ctx.role,
        reason=(body.reason if body else None),
    )
    return success(_variant_out(payload))


@router.get("/jobs/{job_id}/approval-readiness")
async def approval_readiness(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.get_approval_readiness(db, ctx.company_id, job_id)
    return success(ApprovalReadinessOut.model_validate(payload).model_dump(mode="json"))


@router.post("/jobs/{job_id}/approve-all")
async def approve_all_content(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.approve_all(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
    )
    return success(
        {
            "job": JobDetailOut.model_validate(payload["job"]).model_dump(mode="json"),
            "variants": [
                ContentVariantDetailOut.model_validate(v).model_dump(mode="json")
                for v in payload["variants"]
            ],
            "readiness": ApprovalReadinessOut.model_validate(payload["readiness"]).model_dump(
                mode="json"
            ),
        }
    )


@router.post("/jobs/{job_id}/approve")
async def approve_job(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.approve_job(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
    )
    return success(
        {
            "job": JobDetailOut.model_validate(payload["job"]).model_dump(mode="json"),
            "variants": [
                ContentVariantDetailOut.model_validate(v).model_dump(mode="json")
                for v in payload["variants"]
            ],
            "readiness": ApprovalReadinessOut.model_validate(payload["readiness"]).model_dump(
                mode="json"
            ),
        }
    )

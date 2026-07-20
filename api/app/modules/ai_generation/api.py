"""Generation HTTP routes (spec §10.7)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.responses import success
from app.db.session import get_db
from app.modules.ai_generation import service
from app.modules.ai_generation.schemas import (
    ContentVariantOut,
    GenerateRequest,
    GenerationRunOut,
    JobContentOut,
    StructuredDetailsOut,
)
from app.modules.jobs import service as job_service
from app.modules.jobs.schemas import JobDetailOut

router = APIRouter(tags=["generation"])


def _run_out(run) -> dict:
    return GenerationRunOut.model_validate(
        service.serialize_run(run, include_variants=True)
    ).model_dump(mode="json")


def _job_detail(job) -> dict:
    return JobDetailOut.model_validate(job_service.serialize_job_detail(job)).model_dump(
        mode="json"
    )


@router.post("/jobs/{job_id}/generate")
async def generate_content(
    job_id: UUID,
    body: GenerateRequest | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.generate(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        body=body or GenerateRequest(),
    )
    return success(
        {
            "run": GenerationRunOut.model_validate(payload["run"]).model_dump(mode="json"),
            "job": JobDetailOut.model_validate(payload["job"]).model_dump(mode="json"),
            "variants": [
                ContentVariantOut.model_validate(v).model_dump(mode="json")
                for v in payload["variants"]
            ],
            "warnings": payload.get("warnings") or [],
        }
    )


@router.post("/jobs/{job_id}/regenerate")
async def regenerate_content(
    job_id: UUID,
    body: GenerateRequest | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.regenerate(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        body=body or GenerateRequest(),
    )
    return success(
        {
            "run": GenerationRunOut.model_validate(payload["run"]).model_dump(mode="json"),
            "job": JobDetailOut.model_validate(payload["job"]).model_dump(mode="json"),
            "variants": [
                ContentVariantOut.model_validate(v).model_dump(mode="json")
                for v in payload["variants"]
            ],
            "warnings": payload.get("warnings") or [],
        }
    )


@router.get("/jobs/{job_id}/generation-runs")
async def list_generation_runs(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    runs = await service.list_runs(db, ctx.company_id, job_id)
    return success([_run_out(r) for r in runs])


@router.get("/generation-runs/{run_id}")
async def get_generation_run(
    run_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    run = await service.get_run(db, ctx.company_id, run_id)
    return success(_run_out(run))


@router.get("/jobs/{job_id}/content")
async def get_job_content(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.get_job_content(db, ctx.company_id, job_id)
    structured = None
    if payload["structured_details"]:
        structured = StructuredDetailsOut.model_validate(
            payload["structured_details"]
        ).model_dump(mode="json")
    return success(
        JobContentOut(
            job_id=payload["job_id"],
            structured_details=structured,
            variants=[
                ContentVariantOut.model_validate(v) for v in payload["variants"]
            ],
            latest_generation_run_id=payload["latest_generation_run_id"],
            generation_version=payload["generation_version"],
        ).model_dump(mode="json")
    )

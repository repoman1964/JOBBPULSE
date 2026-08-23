"""Soft-delete helpers for contractor jobs."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.core.errors import AppError
from app.models.enums import PublicJobStatus
from app.models.job import Job


def assert_can_delete_job(public_status: str) -> None:
    if public_status == PublicJobStatus.publishing.value:
        raise AppError(
            "job_locked",
            "Wait until publishing finishes before deleting this job.",
            status_code=409,
        )


def mark_job_deleted(job: Any, *, now: datetime) -> None:
    job.deleted_at = now


async def get_visible_job(db: Any, job_id: UUID, company_id: UUID) -> Job:
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.company_id == company_id,
            Job.deleted_at.is_(None),
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise AppError("not_found", "Job not found.", status_code=404)
    return job

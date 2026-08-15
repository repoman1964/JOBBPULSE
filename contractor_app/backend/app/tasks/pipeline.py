"""Celery tasks for content pipeline and publishing."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run(coro):
    return asyncio.run(coro)


async def _with_session(fn, *args):
    async with AsyncSessionLocal() as session:
        try:
            await fn(session, *args)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@celery_app.task(
    name="jobbpulse.process_job_submission",
    bind=True,
    max_retries=5,
    default_retry_delay=30,
)
def process_job_submission(self, job_id: str, submission_id: str) -> str:
    from app.services.engine import run_content_pipeline

    try:
        _run(
            _with_session(
                run_content_pipeline, UUID(job_id), UUID(submission_id)
            )
        )
        return "ok"
    except Exception as exc:
        logger.exception("process_job_submission failed")
        raise self.retry(exc=exc) from exc


@celery_app.task(
    name="jobbpulse.process_revision",
    bind=True,
    max_retries=3,
    default_retry_delay=15,
)
def process_revision(self, revision_id: str) -> str:
    from app.services.engine import apply_asset_revision, apply_description_revision
    from app.models.content import RevisionRequest
    from sqlalchemy import select

    async def _do(session, rid: UUID):
        rev = await session.get(RevisionRequest, rid)
        if rev is None:
            return
        if rev.generated_asset_id is None:
            await apply_description_revision(session, rid)
        else:
            await apply_asset_revision(session, rid)

    try:
        _run(_with_session(_do, UUID(revision_id)))
        return "ok"
    except Exception as exc:
        logger.exception("process_revision failed")
        raise self.retry(exc=exc) from exc


@celery_app.task(
    name="jobbpulse.process_approve_and_publish",
    bind=True,
    max_retries=5,
    default_retry_delay=20,
)
def process_approve_and_publish(
    self, job_id: str, package_id: str, idempotency_key: str
) -> str:
    from app.services.engine import apply_publish

    try:
        _run(
            _with_session(
                apply_publish, UUID(job_id), UUID(package_id), idempotency_key
            )
        )
        return "ok"
    except Exception as exc:
        logger.exception("process_approve_and_publish failed")
        raise self.retry(exc=exc) from exc

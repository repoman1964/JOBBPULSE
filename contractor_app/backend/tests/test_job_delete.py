"""Soft-delete rules for contractor jobs."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.core.errors import AppError
from app.services.job_delete import assert_can_delete_job, mark_job_deleted


def test_blocks_delete_while_publishing() -> None:
    with pytest.raises(AppError) as exc:
        assert_can_delete_job("publishing")
    assert exc.value.status_code == 409
    assert exc.value.code == "job_locked"


@pytest.mark.parametrize("status", ["active", "ready_to_finish", "ready_for_approval", "published"])
def test_allows_delete_in_non_publishing_states(status: str) -> None:
    assert_can_delete_job(status)


def test_mark_job_deleted_sets_timestamp_without_touching_media() -> None:
    now = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)
    job = SimpleNamespace(deleted_at=None, media=["keep-me"])
    mark_job_deleted(job, now=now)
    assert job.deleted_at is now
    assert job.media == ["keep-me"]

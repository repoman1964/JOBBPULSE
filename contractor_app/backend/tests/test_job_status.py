"""Unit tests for public status helpers."""

from __future__ import annotations

import pytest

from app.core.errors import AppError
from app.services.job_status import assert_public_transition, compute_active_public_status


def test_compute_ready_to_finish() -> None:
    status = compute_active_public_status(
        counts={"before": 2, "progress": 0, "after": 2},
        minimums={"before": 2, "progress": 0, "after": 2},
        current="active",
    )
    assert status == "ready_to_finish"


def test_does_not_override_terminal() -> None:
    status = compute_active_public_status(
        counts={"before": 0, "progress": 0, "after": 0},
        minimums={"before": 2, "progress": 0, "after": 2},
        current="processing",
    )
    assert status == "processing"


def test_invalid_transition() -> None:
    with pytest.raises(AppError):
        assert_public_transition("published", "active")

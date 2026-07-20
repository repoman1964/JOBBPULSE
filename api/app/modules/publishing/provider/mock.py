"""Mock social publishing provider for MVP / tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.modules.publishing.provider.base import (
    ConnectResult,
    PublishRequest,
    PublishResult,
    PublishStatus,
    ScheduleRequest,
)

# Shared across process for status lookup (tests + dev)
_STATUS: dict[str, PublishStatus] = {}
# Track publish counts per idempotency key for duplicate detection tests
_IDEMPOTENCY_HITS: dict[str, int] = {}

FAIL_MARKER = "__FAIL_PUBLISH__"


class MockPublishingProvider:
    name = "mock"

    async def connect_account(
        self,
        *,
        platform: str,
        display_name: Optional[str] = None,
        auth_code: Optional[str] = None,
    ) -> ConnectResult:
        ext_id = f"mock_{platform}_{uuid.uuid4().hex[:10]}"
        label = display_name or f"Mock {platform.replace('_', ' ').title()}"
        token = f"mock_token_{uuid.uuid4().hex[:16]}"
        _ = auth_code
        return ConnectResult(
            external_account_id=ext_id,
            display_name=label,
            platform=platform,
            credentials=token,
            raw={"provider": "mock"},
        )

    async def publish_post(self, request: PublishRequest) -> PublishResult:
        key = request.idempotency_key or uuid.uuid4().hex
        _IDEMPOTENCY_HITS[key] = _IDEMPOTENCY_HITS.get(key, 0) + 1

        # Idempotent: if already published successfully for this key, reuse
        existing = _STATUS.get(f"idemp:{key}")
        if existing and existing.status == "published":
            return PublishResult(
                success=True,
                external_id=existing.external_id,
                external_url=existing.external_url,
                status="published",
                raw={"idempotent_replay": True, "hits": _IDEMPOTENCY_HITS[key]},
            )

        if FAIL_MARKER in (request.body or ""):
            ext_id = f"fail_{uuid.uuid4().hex[:8]}"
            result = PublishResult(
                success=False,
                external_id=ext_id,
                status="failed",
                error_message="Mock provider forced failure (__FAIL_PUBLISH__).",
                raw={"provider": "mock", "forced_fail": True},
            )
            _STATUS[ext_id] = PublishStatus(
                external_id=ext_id,
                status="failed",
                error_message=result.error_message,
                raw=result.raw,
            )
            return result

        ext_id = f"post_{uuid.uuid4().hex[:12]}"
        url = f"https://mock.social/{request.platform}/{ext_id}"
        status = PublishStatus(
            external_id=ext_id,
            status="published",
            external_url=url,
            raw={
                "provider": "mock",
                "platform": request.platform,
                "body_len": len(request.body or ""),
                "media_count": len(request.media_urls or []),
            },
        )
        _STATUS[ext_id] = status
        _STATUS[f"idemp:{key}"] = status
        return PublishResult(
            success=True,
            external_id=ext_id,
            external_url=url,
            status="published",
            raw=status.raw,
        )

    async def schedule_post(self, request: ScheduleRequest) -> PublishResult:
        key = request.idempotency_key or uuid.uuid4().hex
        if FAIL_MARKER in (request.body or ""):
            return PublishResult(
                success=False,
                status="failed",
                error_message="Mock provider forced failure on schedule.",
            )
        ext_id = f"sched_{uuid.uuid4().hex[:12]}"
        url = f"https://mock.social/{request.platform}/scheduled/{ext_id}"
        when = request.scheduled_for or datetime.now(timezone.utc)
        status = PublishStatus(
            external_id=ext_id,
            status="scheduled",
            external_url=url,
            raw={
                "provider": "mock",
                "scheduled_for": when.isoformat(),
                "platform": request.platform,
            },
        )
        _STATUS[ext_id] = status
        _STATUS[f"idemp:{key}"] = status
        return PublishResult(
            success=True,
            external_id=ext_id,
            external_url=url,
            status="scheduled",
            raw=status.raw,
        )

    async def get_status(self, external_id: str) -> PublishStatus:
        if external_id in _STATUS:
            return _STATUS[external_id]
        return PublishStatus(
            external_id=external_id,
            status="unknown",
            error_message="Not found in mock store",
        )

    async def verify_connection(
        self, *, platform: str, external_account_id: str, credentials: Optional[str]
    ) -> bool:
        _ = platform
        if not external_account_id:
            return False
        if credentials and credentials.startswith("bad_"):
            return False
        return True


def mock_idempotency_hits(key: str) -> int:
    return _IDEMPOTENCY_HITS.get(key, 0)


def reset_mock_store() -> None:
    _STATUS.clear()
    _IDEMPOTENCY_HITS.clear()

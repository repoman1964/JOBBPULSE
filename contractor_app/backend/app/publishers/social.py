"""Social publisher interface and fake implementation."""

from __future__ import annotations

from uuid import uuid4

from app.publishers.base import PublishResult


class FakeSocialPublisher:
    async def publish(
        self,
        *,
        platform: str,
        title: str,
        body: str,
        media_urls: list[str],
        idempotency_key: str,
    ) -> PublishResult:
        return PublishResult(
            success=True,
            provider_request_id=f"fake-req-{uuid4().hex[:12]}",
            provider_job_id=f"fake-job-{uuid4().hex[:12]}",
            response={
                "platform": platform,
                "idempotencyKey": idempotency_key,
                "status": "ok",
            },
        )

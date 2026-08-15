"""Contractor Conversion Site first-party publisher (fake-capable)."""

from __future__ import annotations

from uuid import UUID, uuid4

from app.core.config import get_settings
from app.publishers.base import PublishResult


class ConversionSitePublisher:
    async def publish(
        self,
        *,
        company_id: UUID,
        job_id: UUID,
        title: str,
        body: str,
        package_version: int,
    ) -> PublishResult:
        settings = get_settings()
        # Live HTTP when configured; otherwise fake success
        if settings.conversion_site_api_url and settings.provider_mode == "live":
            # Placeholder for real HTTP adapter
            pass
        return PublishResult(
            success=True,
            provider_request_id=f"conv-{uuid4().hex[:12]}",
            response={
                "companyId": str(company_id),
                "jobId": str(job_id),
                "version": package_version,
                "title": title,
            },
        )

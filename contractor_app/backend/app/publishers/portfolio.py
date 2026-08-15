"""JobbPulse Portfolio Website first-party publisher."""

from __future__ import annotations

from uuid import UUID, uuid4

from app.core.config import get_settings
from app.publishers.base import PublishResult


class PortfolioSitePublisher:
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
        if settings.portfolio_site_api_url and settings.provider_mode == "live":
            pass
        return PublishResult(
            success=True,
            provider_request_id=f"port-{uuid4().hex[:12]}",
            response={
                "companyId": str(company_id),
                "jobId": str(job_id),
                "version": package_version,
                "title": title,
            },
        )

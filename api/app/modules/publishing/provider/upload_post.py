"""Upload-Post publishing provider (connect URL + live posts)."""

from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import uuid4

import httpx

from app.core.config import get_settings
from app.modules.publishing.provider.base import (
    ConnectResult,
    PublishRequest,
    PublishResult,
    PublishStatus,
    ScheduleRequest,
)

logger = logging.getLogger(__name__)


class UploadPostClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base = (settings.upload_post_base_url or "https://api.upload-post.com/api").rstrip("/")
        self.api_key = (settings.publishing_api_key or "").strip()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Apikey {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_user(self, username: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base}/uploadposts/users",
                headers=self._headers(),
                json={"username": username},
            )
            if resp.status_code == 409:
                return {"username": username, "status": "exists"}
            resp.raise_for_status()
            return resp.json()

    async def generate_connect_url(self, *, username: str, redirect_url: str) -> str:
        await self.create_user(username)
        payload = {
            "username": username,
            "redirect_url": redirect_url,
            "connect_title": "Connect Your Social Accounts",
            "connect_description": "Choose where JobbPulse can publish your completed jobs.",
            "show_calendar": False,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base}/uploadposts/users/generate-jwt",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data.get("url") or data.get("access_url") or data.get("jwt_url") or "")


class UploadPostPublishingProvider:
    name = "upload_post"

    async def connect_account(
        self,
        *,
        platform: str,
        display_name: Optional[str] = None,
        auth_code: Optional[str] = None,
    ) -> ConnectResult:
        settings = get_settings()
        username = (display_name or f"jobbpulse-{platform}-{uuid4().hex[:8]}").replace(" ", "-")
        client = UploadPostClient()
        url = ""
        if client.api_key:
            try:
                url = await client.generate_connect_url(
                    username=username,
                    redirect_url=f"{settings.frontend_url.rstrip('/')}/settings/social-return",
                )
            except Exception:
                logger.exception("Upload-Post connect URL failed")
        ext_id = f"upload_post_{platform}_{uuid4().hex[:10]}"
        return ConnectResult(
            external_account_id=ext_id,
            display_name=display_name or platform,
            platform=platform,
            credentials=auth_code or "",
            raw={"authorize_url": url or None, "provider": "upload_post"},
        )

    async def publish_post(self, request: PublishRequest) -> PublishResult:
        client = UploadPostClient()
        if not client.api_key:
            return PublishResult(
                success=False,
                status="failed",
                error_message="UPLOAD_POST_API_KEY is not set.",
            )
        payload = {
            "platform": request.platform,
            "title": request.title,
            "body": request.body,
            "media_urls": request.media_urls,
            "idempotency_key": request.idempotency_key,
            "external_account_id": request.external_account_id,
        }
        try:
            async with httpx.AsyncClient(timeout=45.0) as http:
                resp = await http.post(
                    f"{client.base}/uploadposts",
                    headers=client._headers(),
                    json=payload,
                )
                if not resp.is_success:
                    return PublishResult(
                        success=False,
                        status="failed",
                        error_message=resp.text[:500],
                        raw={"status_code": resp.status_code},
                    )
                data = resp.json() if resp.content else {}
        except httpx.HTTPError as exc:
            return PublishResult(success=False, status="failed", error_message=str(exc))
        ext_id = str(data.get("id") or data.get("job_id") or uuid4().hex)
        return PublishResult(
            success=True,
            external_id=ext_id,
            external_url=data.get("url"),
            status="published",
            raw=data if isinstance(data, dict) else None,
        )

    async def schedule_post(self, request: ScheduleRequest) -> PublishResult:
        return await self.publish_post(request)

    async def get_status(self, external_id: str) -> PublishStatus:
        return PublishStatus(external_id=external_id, status="published")

    async def verify_connection(
        self, *, platform: str, external_account_id: str, credentials: Optional[str]
    ) -> bool:
        return bool(external_account_id)

"""Upload-Post HTTP client (live mode)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class UploadPostClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base = settings.upload_post_base_url.rstrip("/")
        self.api_key = settings.upload_post_api_key or ""

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
                # Idempotent — profile exists
                return {"username": username, "status": "exists"}
            resp.raise_for_status()
            return resp.json()

    async def generate_connect_url(
        self,
        *,
        username: str,
        redirect_url: str,
    ) -> str:
        # Ensure user exists first
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

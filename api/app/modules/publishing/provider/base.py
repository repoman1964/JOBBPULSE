"""Publishing provider protocol and request/result types (§16)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Protocol


@dataclass
class PublishRequest:
    platform: str
    external_account_id: str
    credentials: Optional[str]
    body: str
    title: Optional[str] = None
    media_urls: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str = ""


@dataclass
class ScheduleRequest(PublishRequest):
    scheduled_for: Optional[datetime] = None


@dataclass
class PublishResult:
    success: bool
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    status: str = "published"  # published | failed | scheduled
    error_message: Optional[str] = None
    raw: Optional[dict[str, Any]] = None


@dataclass
class PublishStatus:
    external_id: str
    status: str
    external_url: Optional[str] = None
    error_message: Optional[str] = None
    raw: Optional[dict[str, Any]] = None


@dataclass
class ConnectResult:
    external_account_id: str
    display_name: str
    platform: str
    credentials: str
    raw: Optional[dict[str, Any]] = None


class PublishingProvider(Protocol):
    name: str

    async def connect_account(
        self,
        *,
        platform: str,
        display_name: Optional[str] = None,
        auth_code: Optional[str] = None,
    ) -> ConnectResult: ...

    async def publish_post(self, request: PublishRequest) -> PublishResult: ...

    async def schedule_post(self, request: ScheduleRequest) -> PublishResult: ...

    async def get_status(self, external_id: str) -> PublishStatus: ...

    async def verify_connection(
        self, *, platform: str, external_account_id: str, credentials: Optional[str]
    ) -> bool: ...

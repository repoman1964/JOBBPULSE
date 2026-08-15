"""Publisher result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PublishResult:
    success: bool
    provider_request_id: str | None = None
    provider_job_id: str | None = None
    response: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None

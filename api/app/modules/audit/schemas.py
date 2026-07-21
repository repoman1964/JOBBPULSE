"""Audit API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    user_id: Optional[UUID] = None
    entity_type: str
    entity_id: UUID
    action: str
    before_json: Optional[dict[str, Any]] = None
    after_json: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AuditEventListOut(BaseModel):
    items: list[AuditEventOut]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)

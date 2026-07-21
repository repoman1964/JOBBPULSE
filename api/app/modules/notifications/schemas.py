"""Notification API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    company_id: UUID
    type: str
    title: str
    body: str
    channel: str
    status: str
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    metadata_json: Optional[dict[str, Any]] = None
    created_at: datetime


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    unread_count: int = Field(ge=0)
    limit: int
    offset: int

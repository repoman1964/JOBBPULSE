"""Pydantic schemas for publishing connections and publish orchestration."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConnectionStart(BaseModel):
    platform: str = Field(min_length=1, max_length=40)
    display_name: Optional[str] = Field(default=None, max_length=200)


class ConnectionCallback(BaseModel):
    connection_id: Optional[UUID] = None
    auth_code: Optional[str] = None
    platform: Optional[str] = None


class JobPublishRequest(BaseModel):
    """Unified publish request (§10.10)."""

    publish_to_directory: bool = True
    social_connection_ids: list[UUID] = Field(default_factory=list)
    scheduled_for: Optional[datetime] = None


class JobScheduleRequest(BaseModel):
    """Schedule social posts; directory publishes immediately if requested."""

    scheduled_for: datetime
    publish_to_directory: bool = False
    social_connection_ids: list[UUID] = Field(default_factory=list)

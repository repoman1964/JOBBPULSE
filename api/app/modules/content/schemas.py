"""Pydantic schemas for content review APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ContentUpdate(BaseModel):
    """Edit draft fields. body_generated is immutable — use body_edited."""

    body_edited: Optional[str] = Field(default=None, max_length=20000)
    title: Optional[str] = Field(default=None, max_length=300)
    call_to_action: Optional[str] = Field(default=None, max_length=300)
    hashtags_json: Optional[list[str]] = None


class RejectRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=2000)


class ContentVariantDetailOut(BaseModel):
    id: UUID
    job_id: UUID
    generation_run_id: UUID
    content_type: str
    platform_target: Optional[str] = None
    title: Optional[str] = None
    body_generated: str
    body_edited: Optional[str] = None
    body_effective: str
    call_to_action: Optional[str] = None
    hashtags_json: Optional[list[Any]] = None
    status: str
    version_number: int
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ApprovalReadinessOut(BaseModel):
    can_approve_job: bool
    blockers: list[str] = Field(default_factory=list)
    soft_warnings: list[str] = Field(default_factory=list)
    social_approved: bool
    directory_approved: bool
    after_count: int = 0
    before_count: int = 0


class ApproveJobResultOut(BaseModel):
    job: dict[str, Any]
    variants: list[ContentVariantDetailOut] = Field(default_factory=list)
    readiness: ApprovalReadinessOut

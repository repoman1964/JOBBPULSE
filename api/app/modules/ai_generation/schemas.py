"""Pydantic schemas for AI generation I/O and API DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Provider I/O ---


class JobGenerationInput(BaseModel):
    """Privacy-safe generation input. Never includes private job title."""

    job_id: str
    company_id: str
    service_key: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    location_display: Optional[str] = None
    transcript: str
    before_count: int = 0
    after_count: int = 0
    total_photo_count: int = 0
    company_name: Optional[str] = None
    company_trade: Optional[str] = None
    default_tone: str = "friendly_local"
    default_call_to_action: Optional[str] = None
    tone: Optional[str] = None
    length_preference: str = "standard"
    user_instruction: Optional[str] = None

    def to_snapshot_dict(self) -> dict[str, Any]:
        """JSON-safe snapshot for generation_runs.input_snapshot_json."""
        return self.model_dump(mode="json")


class StructuredJobDetails(BaseModel):
    customer_problem: Optional[str] = None
    work_completed: Optional[str] = None
    materials: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    techniques: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    result: Optional[str] = None
    duration_text: Optional[str] = None
    customer_reaction: Optional[str] = None
    homeowner_advice: Optional[str] = None
    safety_notes: Optional[str] = None
    location_context: Optional[str] = None
    differentiators: list[str] = Field(default_factory=list)
    confidence_json: dict[str, Any] = Field(default_factory=dict)


class ContentPiece(BaseModel):
    title: Optional[str] = None
    body: str
    hashtags: list[str] = Field(default_factory=list)
    call_to_action: Optional[str] = None
    # directory_listing extras
    summary: Optional[str] = None
    work_completed: Optional[str] = None


class GeneratedContentBundle(BaseModel):
    structured_details: StructuredJobDetails
    content: dict[str, ContentPiece]
    warnings: list[str] = Field(default_factory=list)
    uncertain_claims: list[str] = Field(default_factory=list)
    model_name: str = "mock-v1"
    prompt_version: str = "v1-mock"

    def to_snapshot_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


# --- HTTP request/response ---


class GenerateRequest(BaseModel):
    tone: Optional[str] = Field(default=None, max_length=50)
    length_preference: Optional[str] = Field(default="standard", max_length=40)
    user_instruction: Optional[str] = Field(default=None, max_length=2000)


class ContentVariantOut(BaseModel):
    id: UUID
    job_id: UUID
    generation_run_id: UUID
    content_type: str
    platform_target: Optional[str] = None
    title: Optional[str] = None
    body_generated: str
    body_edited: Optional[str] = None
    call_to_action: Optional[str] = None
    hashtags_json: Optional[list[Any]] = None
    status: str
    version_number: int
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class GenerationRunOut(BaseModel):
    id: UUID
    job_id: UUID
    requested_by: Optional[UUID] = None
    status: str
    generation_type: str
    tone: Optional[str] = None
    length_preference: Optional[str] = None
    user_instruction: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    input_snapshot_json: Optional[dict[str, Any]] = None
    output_snapshot_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    variants: list[ContentVariantOut] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StructuredDetailsOut(BaseModel):
    id: UUID
    job_id: UUID
    generation_run_id: Optional[UUID] = None
    customer_problem: Optional[str] = None
    work_completed: Optional[str] = None
    materials: Optional[list[Any]] = None
    equipment: Optional[list[Any]] = None
    techniques: Optional[list[Any]] = None
    challenges: Optional[list[Any]] = None
    result: Optional[str] = None
    duration_text: Optional[str] = None
    customer_reaction: Optional[str] = None
    homeowner_advice: Optional[str] = None
    safety_notes: Optional[str] = None
    location_context: Optional[str] = None
    differentiators: Optional[list[Any]] = None
    confidence_json: Optional[dict[str, Any]] = None
    source_version: int
    created_at: datetime
    updated_at: datetime


class JobContentOut(BaseModel):
    job_id: UUID
    structured_details: Optional[StructuredDetailsOut] = None
    variants: list[ContentVariantOut] = Field(default_factory=list)
    latest_generation_run_id: Optional[UUID] = None
    generation_version: int = 0

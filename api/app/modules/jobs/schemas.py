"""Job and media request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field, field_validator

# Contractor-facing photo stages for Phase 2 (progress deferred).
STAGE_LABEL_PATTERN = "^(before|progress|after)$"


class JobCreate(BaseModel):
    """Create a Job. `title` is required and private (contractor reference only)."""

    model_config = {"populate_by_name": True}

    title: str = Field(
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("title", "name"),
    )
    service_key: Optional[str] = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("service_key", "serviceType"),
    )
    # Coarse area only — never street address (client may fill from quiet geolocation).
    location_display: Optional[str] = Field(
        default=None,
        max_length=200,
        validation_alias=AliasChoices("location_display", "locationText"),
    )
    city: Optional[str] = Field(default=None, max_length=150)
    state: Optional[str] = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("state", "region"),
    )
    postal_code: Optional[str] = Field(default=None, max_length=20)
    customer_name_private: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("notes", "internalNote"),
    )
    assigned_crew_member: Optional[str] = Field(
        default=None,
        max_length=200,
        validation_alias=AliasChoices("assigned_crew_member", "assignedCrewMember"),
    )

    @field_validator("title")
    @classmethod
    def title_required_non_blank(cls, v: str) -> str:
        cleaned = (v or "").strip()
        if not cleaned:
            raise ValueError("Job name is required.")
        return cleaned


class JobUpdate(BaseModel):
    model_config = {"populate_by_name": True}

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        validation_alias=AliasChoices("title", "name"),
    )
    service_key: Optional[str] = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("service_key", "serviceType"),
    )
    location_display: Optional[str] = Field(
        default=None,
        max_length=200,
        validation_alias=AliasChoices("location_display", "locationText"),
    )
    city: Optional[str] = Field(default=None, max_length=150)
    state: Optional[str] = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("state", "region"),
    )
    postal_code: Optional[str] = Field(default=None, max_length=20)
    customer_name_private: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("notes", "internalNote"),
    )
    assigned_crew_member: Optional[str] = Field(
        default=None,
        max_length=200,
        validation_alias=AliasChoices("assigned_crew_member", "assignedCrewMember"),
    )
    privacy_mode: Optional[str] = Field(default=None, max_length=40)

    @field_validator("title")
    @classmethod
    def title_non_blank_if_set(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Job name cannot be empty.")
        return cleaned


class NextActionOut(BaseModel):
    action: str
    label: str
    cta: str
    reason: str
    optional_tip: Optional[str] = None


class PhotoCountsOut(BaseModel):
    total: int
    before: int
    progress: int = 0
    after: int
    has_before_after_pair: bool


class TimelineStepOut(BaseModel):
    key: str
    label: str
    status: str  # complete | current | upcoming | locked | optional | skipped


class MediaOut(BaseModel):
    id: UUID
    job_id: UUID
    storage_key: str
    url: Optional[str] = None
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    asset_type: str
    stage_label: str
    display_order: int
    is_primary: bool
    processing_status: str
    moderation_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobSummaryOut(BaseModel):
    id: UUID
    title: str  # private contractor label — never for public/AI
    service_key: Optional[str] = None
    location_display: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    status: str
    photo_counts: PhotoCountsOut
    next_action: NextActionOut
    timeline: list[TimelineStepOut]
    created_at: datetime
    updated_at: datetime


class VoiceSummaryOut(BaseModel):
    id: UUID
    job_id: UUID
    audio_asset_id: Optional[UUID] = None
    audio_url: Optional[str] = None
    transcript_raw: Optional[str] = None
    transcript_edited: Optional[str] = None
    transcript: Optional[str] = None
    language: str
    transcription_status: str
    transcription_provider: Optional[str] = None
    transcription_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobDetailOut(BaseModel):
    id: UUID
    company_id: UUID
    created_by: Optional[UUID] = None
    title: str  # private contractor label
    service_key: Optional[str] = None
    location_display: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    customer_name_private: Optional[str] = None
    customer_consent_status: str
    status: str
    notes: Optional[str] = None
    privacy_mode: str
    photo_counts: PhotoCountsOut
    next_action: NextActionOut
    timeline: list[TimelineStepOut]
    media: list[MediaOut]
    voice: Optional[VoiceSummaryOut] = None
    created_at: datetime
    updated_at: datetime
    job_started_at: Optional[datetime] = None
    job_completed_at: Optional[datetime] = None


class MediaUploadUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=300)
    mime_type: str = Field(min_length=3, max_length=100)
    stage_label: str = Field(default="before", pattern=STAGE_LABEL_PATTERN)
    file_size_bytes: Optional[int] = Field(default=None, ge=1, le=50 * 1024 * 1024)


class MediaUploadUrlResponse(BaseModel):
    media_id: UUID
    storage_key: str
    upload_url: str
    upload_method: str = "PUT"
    headers: dict[str, str]
    expires_in: int = 3600
    stage_label: str


class MediaCompleteRequest(BaseModel):
    media_id: UUID
    file_size_bytes: Optional[int] = Field(default=None, ge=1)
    width: Optional[int] = Field(default=None, ge=1)
    height: Optional[int] = Field(default=None, ge=1)


class MediaUpdate(BaseModel):
    stage_label: Optional[str] = Field(default=None, pattern=STAGE_LABEL_PATTERN)
    display_order: Optional[int] = Field(default=None, ge=0)
    is_primary: Optional[bool] = None


class MediaReorderRequest(BaseModel):
    media_ids: list[UUID] = Field(min_length=1)


class VoiceUploadUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=300)
    mime_type: str = Field(min_length=3, max_length=100)
    file_size_bytes: Optional[int] = Field(default=None, ge=1, le=25 * 1024 * 1024)
    duration_seconds: Optional[int] = Field(default=None, ge=0, le=600)
    language: Optional[str] = Field(default="en", max_length=16)


class VoiceUploadUrlResponse(BaseModel):
    media_id: UUID
    storage_key: str
    upload_url: str
    upload_method: str = "PUT"
    headers: dict[str, str]
    expires_in: int = 3600


class VoiceCompleteRequest(BaseModel):
    media_id: UUID
    file_size_bytes: Optional[int] = Field(default=None, ge=1)
    duration_seconds: Optional[int] = Field(default=None, ge=0, le=600)


class VoiceTranscriptUpdate(BaseModel):
    transcript_edited: str = Field(min_length=1)

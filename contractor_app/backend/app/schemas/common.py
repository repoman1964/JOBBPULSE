"""Shared response schemas matching frontend domain types."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PhotoMinimums(APIModel):
    before: int = 1
    progress: int = 0
    after: int = 1


class PhotoMaximums(APIModel):
    before: int = 15
    progress: int = 30
    after: int = 15


class NotificationSettings(APIModel):
    content_ready_for_approval: bool = Field(
        default=True, alias="contentReadyForApproval"
    )
    publishing_complete: bool = Field(default=True, alias="publishingComplete")


class CompanyOut(APIModel):
    id: UUID
    name: str
    contact_name: str = Field(alias="contactName")
    phone: str
    email: str
    website: str
    service_area: str = Field(alias="serviceArea")
    photo_minimums: PhotoMinimums = Field(alias="photoMinimums")
    photo_maximums: PhotoMaximums = Field(alias="photoMaximums")
    notification_settings: NotificationSettings = Field(alias="notificationSettings")


class ContractorOut(APIModel):
    id: UUID
    company_id: UUID = Field(alias="companyId")
    name: str
    email: str
    phone: str
    role: str


class SessionOut(APIModel):
    access_token: str = Field(alias="accessToken")
    contractor: ContractorOut
    company: CompanyOut


class RegisterOut(APIModel):
    email: str
    company_id: UUID = Field(alias="companyId")
    contractor_id: UUID = Field(alias="contractorId")
    verification_url: str | None = Field(default=None, alias="verificationUrl")


class VerifyEmailOut(APIModel):
    email: str
    verified: bool = True


class JobCounts(APIModel):
    before: int = 0
    progress: int = 0
    after: int = 0


class JobOut(APIModel):
    id: UUID
    company_id: UUID = Field(alias="companyId")
    name: str
    service_type: str = Field(alias="serviceType")
    city: str
    region: str = ""
    location_text: str = Field(default="", alias="locationText")
    internal_note: str = Field(default="", alias="internalNote")
    assigned_crew_member: str = Field(default="", alias="assignedCrewMember")
    public_status: str = Field(alias="publicStatus")
    cover_url: str | None = Field(default=None, alias="coverUrl")
    counts: dict[str, int]
    has_voice: bool = Field(alias="hasVoice")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    submitted_at: datetime | None = Field(default=None, alias="submittedAt")
    approved_at: datetime | None = Field(default=None, alias="approvedAt")
    published_at: datetime | None = Field(default=None, alias="publishedAt")


class MediaAssetOut(APIModel):
    id: UUID
    job_id: UUID = Field(alias="jobId")
    kind: str
    photo_category: str | None = Field(default=None, alias="photoCategory")
    url: str
    thumbnail_url: str = Field(alias="thumbnailUrl")
    mime_type: str = Field(alias="mimeType")
    byte_size: int = Field(alias="byteSize")
    duration_ms: int | None = Field(default=None, alias="durationMs")
    upload_status: str = Field(alias="uploadStatus")
    is_favorite: bool = Field(alias="isFavorite")
    is_deleted: bool = Field(alias="isDeleted")
    version: int
    created_at: datetime = Field(alias="createdAt")


class UploadSessionOut(APIModel):
    media_id: UUID = Field(alias="mediaId")
    upload_url: str = Field(alias="uploadUrl")
    expires_at: datetime = Field(alias="expiresAt")


class GeneratedAssetVersionOut(APIModel):
    id: UUID
    version: int
    title: str
    body: str
    preview: dict[str, Any]
    source_media_ids: list[UUID] = Field(alias="sourceMediaIds")
    created_at: datetime = Field(alias="createdAt")


class GeneratedAssetOut(APIModel):
    id: UUID
    package_id: UUID = Field(alias="packageId")
    destination_type: str = Field(alias="destinationType")
    title: str
    body: str
    status: str
    active_version_id: UUID = Field(alias="activeVersionId")
    versions: list[GeneratedAssetVersionOut]
    preview: dict[str, Any]


class ContentPackageOut(APIModel):
    id: UUID
    job_id: UUID = Field(alias="jobId")
    version: int
    status: str
    project_description: str = Field(alias="projectDescription")
    featured_before_media_id: UUID | None = Field(
        default=None, alias="featuredBeforeMediaId"
    )
    featured_after_media_id: UUID | None = Field(
        default=None, alias="featuredAfterMediaId"
    )
    assets: list[GeneratedAssetOut]


class SocialConnectionOut(APIModel):
    platform: str
    status: str
    account_name: str | None = Field(default=None, alias="accountName")
    reason: str | None = None


class ListJobsResult(APIModel):
    items: list[JobOut]
    next_cursor: str | None = Field(default=None, alias="nextCursor")


class ChallengeOut(APIModel):
    challenge_id: UUID = Field(alias="challengeId")
    dev_code: str | None = Field(default=None, alias="devCode")


class ConnectUrlOut(APIModel):
    url: str
    expires_at: datetime = Field(alias="expiresAt")


class HealthOut(APIModel):
    status: str

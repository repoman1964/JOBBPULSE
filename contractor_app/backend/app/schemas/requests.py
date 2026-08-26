"""Request body schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import APIModel, NotificationSettings


class ChallengeRequest(APIModel):
    identifier: str = Field(min_length=3, max_length=255)


class RegisterRequest(APIModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    company_name: str = Field(alias="companyName", min_length=1, max_length=255)
    phone: str | None = None


class LoginRequest(APIModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class VerifyEmailRequest(APIModel):
    token: str = Field(min_length=8, max_length=255)


class ResendVerificationRequest(APIModel):
    email: EmailStr


class VerifyChallengeRequest(APIModel):
    challenge_id: UUID = Field(alias="challengeId")
    code: str = Field(min_length=4, max_length=12)


class UpdateCompanyRequest(APIModel):
    name: str | None = None
    contact_name: str | None = Field(default=None, alias="contactName")
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    service_area: str | None = Field(default=None, alias="serviceArea")


class UpdateNotificationSettingsRequest(APIModel):
    content_ready_for_approval: bool | None = Field(
        default=None, alias="contentReadyForApproval"
    )
    publishing_complete: bool | None = Field(
        default=None, alias="publishingComplete"
    )


class CreateJobRequest(APIModel):
    name: str = Field(min_length=1, max_length=255)
    service_type: str = Field(alias="serviceType", min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=128)
    region: str | None = None
    location_text: str | None = Field(default=None, alias="locationText")
    internal_note: str | None = Field(default=None, alias="internalNote")
    assigned_crew_member: str | None = Field(default=None, alias="assignedCrewMember")


class UpdateJobRequest(APIModel):
    name: str | None = None
    service_type: str | None = Field(default=None, alias="serviceType")
    city: str | None = None
    region: str | None = None
    location_text: str | None = Field(default=None, alias="locationText")
    internal_note: str | None = Field(default=None, alias="internalNote")
    assigned_crew_member: str | None = Field(default=None, alias="assignedCrewMember")


class SubmitJobRequest(APIModel):
    idempotency_key: str = Field(alias="idempotencyKey", min_length=8, max_length=128)


class PhotoUploadSessionRequest(APIModel):
    category: str
    mime_type: str = Field(alias="mimeType")
    byte_size: int = Field(alias="byteSize", ge=1)
    filename: str | None = None
    checksum: str | None = None


class VoiceUploadSessionRequest(APIModel):
    mime_type: str = Field(alias="mimeType")
    byte_size: int = Field(alias="byteSize", ge=1)
    duration_ms: int = Field(alias="durationMs", ge=0)


class UpdateMediaRequest(APIModel):
    is_favorite: bool | None = Field(default=None, alias="isFavorite")
    photo_category: str | None = Field(default=None, alias="photoCategory")


class FeaturedMediaRequest(APIModel):
    featured_before_media_id: UUID = Field(alias="featuredBeforeMediaId")
    featured_after_media_id: UUID = Field(alias="featuredAfterMediaId")


class DescriptionRevisionRequest(APIModel):
    instruction_text: str = Field(alias="instructionText", min_length=1)


class AssetRevisionRequest(APIModel):
    change_type: str = Field(alias="changeType")
    instruction_text: str | None = Field(default=None, alias="instructionText")
    selected_media_ids: list[UUID] | None = Field(
        default=None, alias="selectedMediaIds"
    )


class SelectVersionRequest(APIModel):
    version_id: UUID = Field(alias="versionId")


class ApprovePublishRequest(APIModel):
    idempotency_key: str = Field(alias="idempotencyKey", min_length=8, max_length=128)


# Re-export for convenience
__all__ = [
    "ChallengeRequest",
    "RegisterRequest",
    "LoginRequest",
    "VerifyEmailRequest",
    "ResendVerificationRequest",
    "VerifyChallengeRequest",
    "UpdateCompanyRequest",
    "UpdateNotificationSettingsRequest",
    "CreateJobRequest",
    "UpdateJobRequest",
    "SubmitJobRequest",
    "PhotoUploadSessionRequest",
    "VoiceUploadSessionRequest",
    "UpdateMediaRequest",
    "FeaturedMediaRequest",
    "DescriptionRevisionRequest",
    "AssetRevisionRequest",
    "SelectVersionRequest",
    "ApprovePublishRequest",
    "NotificationSettings",
]

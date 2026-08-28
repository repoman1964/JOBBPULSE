"""Shared enum values for domain models."""

from __future__ import annotations

import enum


class PublicJobStatus(str, enum.Enum):
    active = "active"
    ready_to_finish = "ready_to_finish"
    processing = "processing"
    ready_for_approval = "ready_for_approval"
    needs_revision = "needs_revision"
    publishing = "publishing"
    published = "published"
    publish_issue = "publish_issue"


class InternalJobStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    queued = "queued"
    transcribing = "transcribing"
    curating_media = "curating_media"
    generating = "generating"
    generating_description = "generating_description"
    generating_destinations = "generating_destinations"
    ready_for_approval = "ready_for_approval"
    revision_requested = "revision_requested"
    regenerating = "regenerating"
    approved = "approved"
    publishing = "publishing"
    published = "published"
    partially_failed = "partially_failed"
    failed = "failed"


class PhotoCategory(str, enum.Enum):
    before = "before"
    progress = "progress"
    after = "after"


class MediaKind(str, enum.Enum):
    photo = "photo"
    audio = "audio"


class UploadStatus(str, enum.Enum):
    pending = "pending"
    uploading = "uploading"
    complete = "complete"
    failed = "failed"


class DestinationType(str, enum.Enum):
    facebook = "facebook"
    facebook_group = "facebook_group"
    instagram = "instagram"
    google_business = "google_business"
    tiktok = "tiktok"
    youtube = "youtube"
    x = "x"
    linkedin = "linkedin"
    conversion_site = "conversion_site"
    portfolio_site = "portfolio_site"


class SocialPlatform(str, enum.Enum):
    facebook = "facebook"
    instagram = "instagram"
    google_business = "google_business"


class SocialConnectionStatus(str, enum.Enum):
    connected = "connected"
    not_connected = "not_connected"
    reconnect_required = "reconnect_required"
    connection_pending = "connection_pending"
    provider_unavailable = "provider_unavailable"


class ContractorRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class ContractorStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    invited = "invited"
    disabled = "disabled"


class AccountStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    closed = "closed"


class PackageStatus(str, enum.Enum):
    generating = "generating"
    ready_for_approval = "ready_for_approval"
    revision_requested = "revision_requested"
    approved = "approved"
    publishing = "publishing"
    published = "published"
    failed = "failed"


class AssetStatus(str, enum.Enum):
    ready = "ready"
    regenerating = "regenerating"
    published = "published"
    failed = "failed"


class RevisionChangeType(str, enum.Enum):
    photos = "photos"
    wording = "wording"
    other = "other"
    description = "description"


class RevisionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PublicationStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    succeeded = "succeeded"
    failed = "failed"
    skipped = "skipped"


class WebhookProcessingStatus(str, enum.Enum):
    received = "received"
    processed = "processed"
    failed = "failed"
    ignored = "ignored"

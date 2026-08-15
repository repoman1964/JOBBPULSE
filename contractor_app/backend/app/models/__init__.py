"""Import all models so Alembic and metadata see them."""

from app.models.auth import AuthChallenge, AuthIdentity, RefreshToken
from app.models.company import Company, Contractor
from app.models.content import (
    ContentPackage,
    GeneratedAsset,
    GeneratedAssetVersion,
    RevisionRequest,
)
from app.models.job import Job, JobEvent, JobSubmission
from app.models.media import MediaAsset
from app.models.social import (
    PublicationAttempt,
    SocialConnection,
    SocialProfile,
    WebhookEvent,
)

__all__ = [
    "Company",
    "Contractor",
    "AuthIdentity",
    "AuthChallenge",
    "RefreshToken",
    "Job",
    "JobSubmission",
    "JobEvent",
    "MediaAsset",
    "ContentPackage",
    "GeneratedAsset",
    "GeneratedAssetVersion",
    "RevisionRequest",
    "SocialProfile",
    "SocialConnection",
    "PublicationAttempt",
    "WebhookEvent",
]

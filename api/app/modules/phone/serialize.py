"""CamelCase contractor-app payloads (inside the api/ envelope)."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from uuid import UUID

from app.core import storage as storage_svc
from app.db.models import (
    Company,
    CompanyMembership,
    ContentVariant,
    ContentVariantStatus,
    Job,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    User,
    VoiceSummary,
)
from app.modules.jobs import service as job_service
from app.modules.jobs import state as job_state
from app.modules.phone.status import to_public

DEFAULT_PHOTO_MINS = {"before": 1, "progress": 0, "after": 1}
DEFAULT_PHOTO_MAXS = {"before": 15, "progress": 30, "after": 15}


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _uid(value) -> str:
    return str(value)


def company_out(company: Company, *, owner: Optional[User] = None) -> dict[str, Any]:
    mins = dict(DEFAULT_PHOTO_MINS)
    mins.update(company.photo_minimums_json or {})
    maxs = dict(DEFAULT_PHOTO_MAXS)
    maxs.update(company.photo_maximums_json or {})
    notes = company.notification_settings_json or {}
    return {
        "id": _uid(company.id),
        "name": company.name,
        "contactName": company.contact_name or (owner.full_name if owner else ""),
        "phone": company.phone or (owner.phone if owner else "") or "",
        "email": company.email or (owner.email if owner else "") or "",
        "website": company.website_url or "",
        "serviceArea": company.service_area or "",
        "photoMinimums": {
            "before": int(mins.get("before", 1)),
            "progress": int(mins.get("progress", 0)),
            "after": int(mins.get("after", 1)),
        },
        "photoMaximums": {
            "before": int(maxs.get("before", 15)),
            "progress": int(maxs.get("progress", 30)),
            "after": int(maxs.get("after", 15)),
        },
        "notificationSettings": {
            "contentReadyForApproval": bool(notes.get("contentReadyForApproval", True)),
            "publishingComplete": bool(notes.get("publishingComplete", True)),
        },
    }


def contractor_out(user: User, company: Company, membership: Optional[CompanyMembership]) -> dict[str, Any]:
    role = membership.role.value if membership is not None else "owner"
    return {
        "id": _uid(user.id),
        "companyId": _uid(company.id),
        "name": user.full_name,
        "email": user.email,
        "phone": user.phone or "",
        "role": role,
    }


def session_out(
    *,
    access_token: str,
    user: User,
    company: Company,
    membership: Optional[CompanyMembership],
    refresh_token: Optional[str] = None,
) -> dict[str, Any]:
    """Phone session plus legacy TokenPair fields so existing tests still work."""
    contractor = contractor_out(user, company, membership)
    company_payload = company_out(company, owner=user)
    return {
        "accessToken": access_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "contractor": contractor,
        "company": company_payload,
        "user": {
            "id": _uid(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "last_login_at": _iso(user.last_login_at),
            "created_at": _iso(user.created_at),
        },
        "membership": {
            "id": _uid(membership.id),
            "company_id": _uid(membership.company_id),
            "role": membership.role.value,
            "status": membership.status.value,
        }
        if membership
        else None,
    }


def _signed_media_url(media: Optional[MediaAsset]) -> Optional[str]:
    if media is None:
        return None
    if media.processing_status == MediaProcessingStatus.pending_upload:
        return None
    try:
        return storage_svc.public_or_signed_url(media.storage_key) or None
    except Exception:  # noqa: BLE001
        return None


def pick_featured_photos(job: Job) -> tuple[Optional[MediaAsset], Optional[MediaAsset]]:
    """Favorite / primary / first ready photo per stage, honoring saved featured ids."""
    photos = [
        m
        for m in job_service._ready_media(job)
        if m.asset_type == MediaAssetType.image
    ]

    def pick(stage: MediaStageLabel, preferred_id) -> Optional[MediaAsset]:
        staged = [m for m in photos if m.stage_label == stage]
        if preferred_id:
            hit = next((m for m in staged if m.id == preferred_id), None)
            if hit is not None:
                return hit
        return next((m for m in staged if m.is_favorite), None) or next(
            (m for m in staged if m.is_primary), None
        ) or (staged[0] if staged else None)

    return (
        pick(MediaStageLabel.before, job.featured_before_media_id),
        pick(MediaStageLabel.after, job.featured_after_media_id),
    )


def preview_for_job(job: Optional[Job], *, hashtags: Optional[list[Any]] = None) -> dict[str, Any]:
    before, after = pick_featured_photos(job) if job is not None else (None, None)
    before_url = _signed_media_url(before)
    after_url = _signed_media_url(after)
    return {
        "hashtags": hashtags or [],
        "beforeUrl": before_url,
        "afterUrl": after_url,
        "coverUrl": after_url or before_url,
        "sourceMediaIds": [_uid(m.id) for m in (before, after) if m is not None],
    }


def _cover_url(job: Job) -> Optional[str]:
    preview = preview_for_job(job)
    if preview["coverUrl"]:
        return preview["coverUrl"]
    photos = [
        m
        for m in job_service._ready_media(job)
        if m.asset_type == MediaAssetType.image
    ]
    for stage in (MediaStageLabel.progress,):
        for m in photos:
            if m.stage_label == stage:
                return _signed_media_url(m)
    return None


def _has_voice(job: Job) -> bool:
    voice = job.voice_summary
    if voice is None:
        return False
    asset = voice.audio_asset
    if asset is None:
        return job_state.has_usable_transcript(voice)
    return asset.processing_status != MediaProcessingStatus.pending_upload and asset.deleted_at is None


def job_out(job: Job) -> dict[str, Any]:
    counts = job_state.count_photos(job_service._ready_media(job))
    location = job.location_display or ", ".join(p for p in [job.city, job.state] if p) or ""
    payload = {
        "id": _uid(job.id),
        "companyId": _uid(job.company_id),
        "name": job.title,
        "title": job.title,
        "serviceType": job.service_key or "",
        "service_key": job.service_key,
        "city": job.city or "",
        "region": job.state or "",
        "state": job.state,
        "locationText": location,
        "location_display": job.location_display,
        "internalNote": job.notes or "",
        "notes": job.notes,
        "assignedCrewMember": job.assigned_crew_member or "",
        "publicStatus": to_public(job.status),
        "internalStatus": job.status.value,
        "status": job.status.value,
        "coverUrl": _cover_url(job),
        "counts": {
            "before": counts.before,
            "progress": counts.progress,
            "after": counts.after,
        },
        "photo_counts": job_service.serialize_photo_counts(job),
        "hasVoice": _has_voice(job),
        "next_action": job_service.serialize_next_action(job),
        "timeline": job_service.serialize_timeline(job),
        "createdAt": _iso(job.created_at),
        "updatedAt": _iso(job.updated_at),
        "submittedAt": _iso(job.submitted_at),
        "approvedAt": _iso(job.approved_at),
        "publishedAt": _iso(job.published_at),
        "deletedAt": _iso(job.deleted_at),
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
    return payload


def job_detail_out(job: Job) -> dict[str, Any]:
    """Existing JobDetailOut fields plus phone Job fields."""
    base = job_service.serialize_job_detail(job)
    base.update(job_out(job))
    return base


def _upload_status(media: MediaAsset) -> str:
    if media.processing_status == MediaProcessingStatus.pending_upload:
        return "pending"
    if media.processing_status == MediaProcessingStatus.failed:
        return "failed"
    return "complete"


def media_out(media: MediaAsset) -> dict[str, Any]:
    url = ""
    if media.processing_status != MediaProcessingStatus.pending_upload:
        try:
            url = storage_svc.public_or_signed_url(media.storage_key) or ""
        except Exception:  # noqa: BLE001
            url = ""
    category = None
    if media.asset_type == MediaAssetType.image and media.stage_label != MediaStageLabel.unclassified:
        category = media.stage_label.value
    version = 1
    if media.metadata_json and isinstance(media.metadata_json.get("version"), int):
        version = media.metadata_json["version"]
    return {
        "id": _uid(media.id),
        "jobId": _uid(media.job_id),
        "kind": "audio" if media.asset_type == MediaAssetType.audio else "photo",
        "photoCategory": category,
        "url": url,
        "thumbnailUrl": url,
        "mimeType": media.mime_type or "",
        "byteSize": media.file_size_bytes or 0,
        "durationMs": int((media.duration_seconds or 0) * 1000) if media.duration_seconds else None,
        "uploadStatus": _upload_status(media),
        "isFavorite": bool(media.is_favorite),
        "isDeleted": media.deleted_at is not None,
        "version": version,
        "createdAt": _iso(media.created_at),
    }


def upload_session_out(payload: dict[str, Any]) -> dict[str, Any]:
    expires = datetime.now(timezone.utc) + timedelta(seconds=int(payload.get("expires_in") or 3600))
    return {
        "mediaId": str(payload["media_id"]),
        "uploadUrl": payload["upload_url"],
        "expiresAt": expires.isoformat(),
        "headers": payload.get("headers") or {},
        "objectKey": payload.get("storage_key"),
    }


def voice_as_media(voice: Optional[VoiceSummary]) -> Optional[dict[str, Any]]:
    if voice is None:
        return None
    asset = voice.audio_asset
    if asset is None:
        return None
    return media_out(asset)


DESTINATION_BY_CONTENT_TYPE = {
    "primary_social": "facebook",
    "short_caption": "instagram",
    "before_after": "conversion_site",
    "directory_listing": "portfolio_site",
}

PHONE_DEST_FROM_PLATFORM = {
    "facebook": "facebook",
    "facebook_page": "facebook",
    "instagram": "instagram",
    "google_business": "google_business",
    "facebook_group": "facebook_group",
    "conversion_site": "conversion_site",
    "website_carousel": "conversion_site",
    "website_job_page": "conversion_site",
    "portfolio_site": "portfolio_site",
    "directory": "portfolio_site",
    "directory_page": "portfolio_site",
}


def _dest_for_variant(v: ContentVariant) -> str:
    if v.platform_target:
        return PHONE_DEST_FROM_PLATFORM.get(v.platform_target, v.platform_target)
    return DESTINATION_BY_CONTENT_TYPE.get(v.content_type.value, v.content_type.value)


def asset_out(variant: ContentVariant, *, siblings: list[ContentVariant], job: Optional[Job] = None) -> dict[str, Any]:
    job = job or getattr(variant, "job", None)
    versions = sorted(siblings, key=lambda x: (x.version_number, x.created_at))
    version_payloads = []
    for i, s in enumerate(versions, start=1):
        body = (s.body_edited or s.body_generated or "").strip()
        preview = preview_for_job(job, hashtags=s.hashtags_json or [])
        version_payloads.append(
            {
                "id": _uid(s.id),
                "version": s.version_number or i,
                "title": s.title or "",
                "body": body,
                "preview": preview,
                "sourceMediaIds": preview["sourceMediaIds"],
                "createdAt": _iso(s.created_at),
            }
        )
    active = next((s for s in reversed(versions) if s.status != ContentVariantStatus.superseded), variant)
    body = (active.body_edited or active.body_generated or "").strip()
    preview = preview_for_job(job, hashtags=active.hashtags_json or [])
    return {
        "id": _uid(active.id),
        "packageId": _uid(active.generation_run_id),
        "destinationType": _dest_for_variant(active),
        "title": active.title or "",
        "body": body,
        "status": active.status.value,
        "activeVersionId": _uid(active.id),
        "versions": version_payloads,
        "preview": preview,
    }


def package_out(job: Job, variants: list[ContentVariant]) -> Optional[dict[str, Any]]:
    active = [v for v in variants if v.status != ContentVariantStatus.superseded]
    if not active and not variants:
        return None
    source = active or variants
    run_id = source[0].generation_run_id
    groups: dict[str, list[ContentVariant]] = {}
    all_for_job: dict[str, list[ContentVariant]] = {}
    for v in variants:
        dest = _dest_for_variant(v)
        all_for_job.setdefault(dest, []).append(v)
    for v in source:
        dest = _dest_for_variant(v)
        groups.setdefault(dest, []).append(v)
    assets = [
        asset_out(group[-1], siblings=all_for_job.get(dest, group), job=job)
        for dest, group in groups.items()
    ]
    directory = next((a for a in assets if a["destinationType"] in {"portfolio_site", "directory"}), None)
    description = directory["body"] if directory else (assets[0]["body"] if assets else "")
    version = job.generation_version or 1
    before, after = pick_featured_photos(job)
    return {
        "id": _uid(run_id),
        "jobId": _uid(job.id),
        "version": version,
        "status": "ready" if job.status.value in {"awaiting_review", "approved"} else job.status.value,
        "projectDescription": description,
        "featuredBeforeMediaId": _uid(before.id) if before else None,
        "featuredAfterMediaId": _uid(after.id) if after else None,
        "assets": assets,
    }

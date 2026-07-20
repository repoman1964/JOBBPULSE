"""Strip private fields before sending content to social providers."""

from __future__ import annotations

import json
from typing import Any, Optional

from app.core import storage as storage_svc
from app.db.models import ContentVariant, Job, MediaAsset, MediaAssetType, MediaProcessingStatus
from app.modules.content.service import effective_body


def media_urls_for_social(job: Job, *, limit: int = 10) -> list[str]:
    urls: list[str] = []
    assets = list(job.media_assets or [])
    # Prefer after, then before
    ordered: list[MediaAsset] = []
    ordered.extend(
        m
        for m in assets
        if m.asset_type == MediaAssetType.image
        and m.processing_status != MediaProcessingStatus.pending_upload
        and m.stage_label.value == "after"
    )
    ordered.extend(
        m
        for m in assets
        if m.asset_type == MediaAssetType.image
        and m.processing_status != MediaProcessingStatus.pending_upload
        and m.stage_label.value == "before"
    )
    for media in ordered[:limit]:
        try:
            url = storage_svc.public_or_signed_url(media.storage_key)
            if url:
                urls.append(url)
        except Exception:  # noqa: BLE001
            continue
    return urls


def build_social_payload(
    job: Job,
    variant: ContentVariant,
    *,
    media_urls: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Safe payload for third-party social poster. Never includes private job title."""
    body = effective_body(variant)
    title = (variant.title or "").strip() or None
    private_title = (job.title or "").strip()
    if title and private_title and private_title in title:
        title = None
    if private_title and private_title in body:
        # Do not send private title if it leaked into body
        body = body.replace(private_title, "").strip()

    payload: dict[str, Any] = {
        "body": body,
        "title": title,
        "content_type": variant.content_type.value,
        "service_key": job.service_key,
        "city": job.city,
        "state": job.state,
        "location_display": job.location_display,
        "media_urls": media_urls if media_urls is not None else media_urls_for_social(job),
        "call_to_action": variant.call_to_action,
        "hashtags": variant.hashtags_json,
        # Intentionally omit: job.title, customer_name_private, notes, storage_key
    }
    return payload


def assert_no_private_title(payload: dict[str, Any], private_title: str) -> None:
    if not private_title:
        return
    blob = json.dumps(payload, default=str)
    if private_title in blob:
        raise ValueError("Private job title must not appear in social provider payload.")


def serialize_connection(conn) -> dict[str, Any]:
    """Admin-facing connection — never expose credentials_encrypted."""
    return {
        "id": conn.id,
        "company_id": conn.company_id,
        "provider": conn.provider,
        "platform": conn.platform,
        "external_account_id": conn.external_account_id,
        "display_name": conn.display_name,
        "status": conn.status.value,
        "last_verified_at": conn.last_verified_at,
        "last_error": conn.last_error,
        "created_at": conn.created_at,
        "updated_at": conn.updated_at,
    }


def serialize_publication(pub) -> dict[str, Any]:
    return {
        "id": pub.id,
        "job_id": pub.job_id,
        "content_variant_id": pub.content_variant_id,
        "destination_type": pub.destination_type.value,
        "publishing_connection_id": pub.publishing_connection_id,
        "provider": pub.provider,
        "scheduled_for": pub.scheduled_for,
        "status": pub.status.value,
        "idempotency_key": pub.idempotency_key,
        "provider_request_id": pub.provider_request_id,
        "external_url": pub.external_url,
        "attempt_count": pub.attempt_count,
        "last_error": pub.last_error,
        "published_at": pub.published_at,
        "created_at": pub.created_at,
        "updated_at": pub.updated_at,
    }

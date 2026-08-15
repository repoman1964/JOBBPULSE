"""Social connections and Upload-Post webhooks."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Request
from sqlalchemy import select

from app.core.config import get_settings
from app.core.deps import CurrentAuth, DbSession
from app.core.errors import AppError
from app.models.enums import SocialConnectionStatus, SocialPlatform, WebhookProcessingStatus
from app.models.social import SocialConnection, SocialProfile, WebhookEvent
from app.schemas.common import ConnectUrlOut, SocialConnectionOut
from app.services.mappers import social_to_out

logger = logging.getLogger(__name__)
router = APIRouter(tags=["social"])

PLATFORMS = [p.value for p in SocialPlatform]


@router.get("/social/connections", response_model=list[SocialConnectionOut])
async def list_connections(auth: CurrentAuth, db: DbSession) -> list[SocialConnectionOut]:
    result = await db.execute(
        select(SocialConnection).where(SocialConnection.company_id == auth.company_id)
    )
    existing = {c.platform: c for c in result.scalars().all()}
    # Ensure all platforms represented
    out: list[SocialConnectionOut] = []
    for platform in PLATFORMS:
        conn = existing.get(platform)
        if conn is None:
            out.append(
                SocialConnectionOut(
                    platform=platform,
                    status=SocialConnectionStatus.not_connected.value,
                    accountName=None,
                    reason=None,
                )
            )
        else:
            out.append(social_to_out(conn))
    return out


@router.post("/social/connect-url", response_model=ConnectUrlOut)
async def get_connect_url(auth: CurrentAuth, db: DbSession) -> ConnectUrlOut:
    settings = get_settings()
    # Ensure social profile
    result = await db.execute(
        select(SocialProfile).where(
            SocialProfile.company_id == auth.company_id,
            SocialProfile.provider == "upload_post",
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        username = f"jp_{str(auth.company_id).replace('-', '')[:24]}"
        profile = SocialProfile(
            company_id=auth.company_id,
            provider="upload_post",
            provider_username=username,
            status="active",
        )
        db.add(profile)
        await db.flush()
        # Seed not-connected rows
        for platform in PLATFORMS:
            db.add(
                SocialConnection(
                    company_id=auth.company_id,
                    social_profile_id=profile.id,
                    platform=platform,
                    status=SocialConnectionStatus.not_connected.value,
                )
            )
        await db.flush()

    # Live Upload-Post path when configured; otherwise deterministic fake URL
    expires_at = datetime.now(UTC) + timedelta(minutes=15)
    if settings.provider_mode == "live" and settings.upload_post_api_key:
        from app.integrations.upload_post.client import UploadPostClient

        client = UploadPostClient(settings)
        url = await client.generate_connect_url(
            username=profile.provider_username,
            redirect_url=f"{settings.frontend_base_url}/settings/social-return",
        )
    else:
        # Fake connect URL that frontend can open; social-return completes via mock helper
        url = (
            f"{settings.frontend_base_url}/settings/social-return"
            f"?status=connected&provider=upload_post&fake=1"
        )

    return ConnectUrlOut(url=url, expiresAt=expires_at)


@router.post("/webhooks/upload-post", status_code=204)
async def upload_post_webhook(request: Request, db: DbSession) -> None:
    settings = get_settings()
    # Optional path token
    token = request.query_params.get("token")
    if settings.upload_post_webhook_token and token != settings.upload_post_webhook_token:
        raise AppError("forbidden", "Invalid webhook token.", status_code=403)

    payload: dict[str, Any] = await request.json()
    event_type = str(payload.get("event") or payload.get("type") or "unknown")
    provider_event_id = str(
        payload.get("id")
        or payload.get("event_id")
        or hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    )

    # Idempotent insert
    result = await db.execute(
        select(WebhookEvent).where(
            WebhookEvent.provider == "upload_post",
            WebhookEvent.provider_event_id == provider_event_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        return

    event = WebhookEvent(
        provider="upload_post",
        provider_event_id=provider_event_id,
        event_type=event_type,
        payload_json=payload,
        processing_status=WebhookProcessingStatus.received.value,
    )
    db.add(event)
    await db.flush()

    try:
        await _process_social_webhook(db, event_type, payload)
        event.processing_status = WebhookProcessingStatus.processed.value
        event.processed_at = datetime.now(UTC)
    except Exception as exc:
        logger.exception("webhook processing failed")
        event.processing_status = WebhookProcessingStatus.failed.value
        event.error_message = str(exc)[:500]
        event.processed_at = datetime.now(UTC)


async def _process_social_webhook(
    db: DbSession, event_type: str, payload: dict[str, Any]
) -> None:
    username = payload.get("username") or payload.get("user") or payload.get("profile")
    platform = payload.get("platform") or payload.get("social_platform")
    if not username or not platform:
        return

    result = await db.execute(
        select(SocialProfile).where(SocialProfile.provider_username == str(username))
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return

    result = await db.execute(
        select(SocialConnection).where(
            SocialConnection.social_profile_id == profile.id,
            SocialConnection.platform == str(platform),
        )
    )
    conn = result.scalar_one_or_none()
    if conn is None:
        conn = SocialConnection(
            company_id=profile.company_id,
            social_profile_id=profile.id,
            platform=str(platform),
            status=SocialConnectionStatus.not_connected.value,
        )
        db.add(conn)

    if event_type in {"social_account.connected", "account.connected"}:
        conn.status = SocialConnectionStatus.connected.value
        conn.provider_account_name = payload.get("account_name") or payload.get("name")
        conn.provider_account_id = (
            str(payload.get("account_id")) if payload.get("account_id") else None
        )
        conn.reason = None
    elif event_type in {"social_account.disconnected", "account.disconnected"}:
        conn.status = SocialConnectionStatus.not_connected.value
        conn.provider_account_name = None
        conn.reason = "Disconnected"
    elif event_type in {"social_account.reauth_required", "account.reauth_required"}:
        conn.status = SocialConnectionStatus.reconnect_required.value
        conn.reason = "Reconnect required"
    conn.last_event_at = datetime.now(UTC)

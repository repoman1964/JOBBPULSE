"""Phone-path aliases that the contractor Nuxt client already calls."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from pydantic import AliasChoices, BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AuthContext, get_auth_context
from app.core.exceptions import AppError
from app.core.responses import success
from app.db.models import MediaAssetType
from app.db.session import get_db
from app.modules.jobs import service as job_service
from app.modules.jobs import voice as voice_svc
from app.modules.phone import serialize, service
from app.modules.publishing import service as publishing_service

router = APIRouter(tags=["contractor-app"])


class IdempotencyBody(BaseModel):
    model_config = {"populate_by_name": True}
    idempotency_key: str = Field(validation_alias=AliasChoices("idempotencyKey", "idempotency_key"), min_length=1)


class PhotoSessionBody(BaseModel):
    model_config = {"populate_by_name": True}
    category: str
    mime_type: str = Field(validation_alias=AliasChoices("mimeType", "mime_type"))
    byte_size: int = Field(validation_alias=AliasChoices("byteSize", "byte_size", "file_size_bytes"))
    filename: Optional[str] = None


class VoiceSessionBody(BaseModel):
    model_config = {"populate_by_name": True}
    mime_type: str = Field(validation_alias=AliasChoices("mimeType", "mime_type"))
    byte_size: int = Field(validation_alias=AliasChoices("byteSize", "byte_size", "file_size_bytes"))
    duration_ms: int = Field(default=0, validation_alias=AliasChoices("durationMs", "duration_ms"))


class MediaPatchBody(BaseModel):
    model_config = {"populate_by_name": True}
    is_favorite: Optional[bool] = Field(default=None, validation_alias=AliasChoices("isFavorite", "is_favorite"))
    photo_category: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("photoCategory", "photo_category")
    )


class FeaturedBody(BaseModel):
    model_config = {"populate_by_name": True}
    featured_before_media_id: UUID = Field(
        validation_alias=AliasChoices("featuredBeforeMediaId", "featured_before_media_id")
    )
    featured_after_media_id: UUID = Field(
        validation_alias=AliasChoices("featuredAfterMediaId", "featured_after_media_id")
    )


class InstructionBody(BaseModel):
    model_config = {"populate_by_name": True}
    instruction_text: str = Field(
        default="",
        validation_alias=AliasChoices("instructionText", "instruction_text", "instruction"),
    )
    change_type: Optional[str] = Field(default=None, validation_alias=AliasChoices("changeType", "change_type"))


class SelectVersionBody(BaseModel):
    model_config = {"populate_by_name": True}
    version_id: UUID = Field(validation_alias=AliasChoices("versionId", "version_id"))


class ConnectSocialBody(BaseModel):
    model_config = {"populate_by_name": True}
    account_name: str = Field(default="", validation_alias=AliasChoices("accountName", "account_name"))


class CompanySettingsBody(BaseModel):
    model_config = {"populate_by_name": True}
    content_ready_for_approval: Optional[bool] = Field(
        default=None, validation_alias=AliasChoices("contentReadyForApproval", "content_ready_for_approval")
    )
    publishing_complete: Optional[bool] = Field(
        default=None, validation_alias=AliasChoices("publishingComplete", "publishing_complete")
    )


def _ok(data):
    return success(jsonable_encoder(data, custom_encoder={UUID: str}))


@router.post("/jobs/{job_id}/submit")
async def submit_job(
    job_id: UUID,
    body: IdempotencyBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.submit_job(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        idempotency_key=body.idempotency_key,
    )
    return _ok(serialize.job_out(job))


@router.get("/jobs/{job_id}/package")
async def get_package(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    pkg = await service.get_package(db, ctx.company_id, job_id)
    return _ok(pkg)


@router.patch("/jobs/{job_id}/package/featured-media")
async def featured_media(
    job_id: UUID,
    body: FeaturedBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    pkg = await service.update_featured_media(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        before_id=body.featured_before_media_id,
        after_id=body.featured_after_media_id,
        role=ctx.role,
    )
    return _ok(pkg)


@router.post("/jobs/{job_id}/package/description-revision")
async def description_revision(
    job_id: UUID,
    body: InstructionBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    pkg = await service.request_description_revision(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        instruction=body.instruction_text,
    )
    return _ok(pkg)


@router.get("/generated-assets/{asset_id}")
async def get_asset(
    asset_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(await service.get_asset(db, ctx.company_id, asset_id))


@router.post("/generated-assets/{asset_id}/revisions")
async def revise_asset(
    asset_id: UUID,
    body: InstructionBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.revise_asset(
            db,
            company_id=ctx.company_id,
            asset_id=asset_id,
            user_id=ctx.user_id,
            role=ctx.role,
            instruction=body.instruction_text or "",
        )
    )


@router.post("/generated-assets/{asset_id}/select-version")
async def select_version(
    asset_id: UUID,
    body: SelectVersionBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.select_asset_version(
            db,
            company_id=ctx.company_id,
            asset_id=asset_id,
            version_id=body.version_id,
            role=ctx.role,
        )
    )


@router.post("/jobs/{job_id}/approve-and-publish")
async def approve_and_publish(
    job_id: UUID,
    body: IdempotencyBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    job = await service.approve_and_publish(
        db,
        company_id=ctx.company_id,
        job_id=job_id,
        user_id=ctx.user_id,
        role=ctx.role,
        idempotency_key=body.idempotency_key,
    )
    return _ok(serialize.job_out(job))


@router.post("/jobs/{job_id}/media/upload-sessions", status_code=201)
async def photo_session(
    job_id: UUID,
    body: PhotoSessionBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.create_photo_session(
            db,
            company_id=ctx.company_id,
            job_id=job_id,
            user_id=ctx.user_id,
            role=ctx.role,
            category=body.category,
            mime_type=body.mime_type,
            byte_size=body.byte_size,
            filename=body.filename,
        )
    )


@router.post("/jobs/{job_id}/media/{media_id}/complete")
async def complete_photo(
    job_id: UUID,
    media_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.complete_photo(
            db,
            company_id=ctx.company_id,
            job_id=job_id,
            media_id=media_id,
            role=ctx.role,
        )
    )


@router.patch("/jobs/{job_id}/media/{media_id}")
async def patch_media(
    job_id: UUID,
    media_id: UUID,
    body: MediaPatchBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    _ = job_id
    return _ok(
        await service.patch_media_phone(
            db,
            company_id=ctx.company_id,
            media_id=media_id,
            role=ctx.role,
            is_favorite=body.is_favorite,
            photo_category=body.photo_category,
        )
    )


@router.delete("/jobs/{job_id}/media/{media_id}")
async def delete_media(
    job_id: UUID,
    media_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    _ = job_id
    await job_service.delete_media(db, company_id=ctx.company_id, media_id=media_id, role=ctx.role)
    return _ok({"deleted": True})


@router.post("/jobs/{job_id}/voice/upload-sessions", status_code=201)
async def voice_session(
    job_id: UUID,
    body: VoiceSessionBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.create_voice_session(
            db,
            company_id=ctx.company_id,
            job_id=job_id,
            user_id=ctx.user_id,
            role=ctx.role,
            mime_type=body.mime_type,
            byte_size=body.byte_size,
            duration_ms=body.duration_ms,
        )
    )


@router.post("/jobs/{job_id}/voice/{media_id}/complete")
async def complete_voice(
    job_id: UUID,
    media_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.complete_voice(
            db,
            company_id=ctx.company_id,
            job_id=job_id,
            media_id=media_id,
            role=ctx.role,
        )
    )


@router.get("/social/connections")
async def list_social(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    rows = await publishing_service.list_connections(db, ctx.company_id)
    return _ok(service.social_connections_out(rows))


@router.put("/social/connections/{platform}")
async def connect_social(
    platform: str,
    body: ConnectSocialBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(
        await service.upsert_social_connection(
            db,
            company_id=ctx.company_id,
            role=ctx.role,
            platform=platform,
            account_name=body.account_name,
        )
    )


@router.post("/social/connections/{platform}/disconnect")
async def disconnect_social(
    platform: str,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    return _ok(await service.disconnect_social(db, company_id=ctx.company_id, platform=platform))


@router.post("/social/connect-url")
async def connect_url(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    payload = await publishing_service.start_connection(
        db,
        company_id=ctx.company_id,
        role=ctx.role,
        platform="facebook",
        display_name=None,
    )
    from datetime import datetime, timedelta, timezone

    return _ok(
        {
            "url": payload.get("authorize_url") or payload.get("url") or "https://example.invalid/connect",
            "expiresAt": (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat(),
        }
    )


@router.patch("/company/settings")
async def company_settings(
    body: CompanySettingsBody,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
):
    notes = dict(ctx.company.notification_settings_json or {})
    data = body.model_dump(exclude_unset=True)
    if "content_ready_for_approval" in data and data["content_ready_for_approval"] is not None:
        notes["contentReadyForApproval"] = data["content_ready_for_approval"]
    if "publishing_complete" in data and data["publishing_complete"] is not None:
        notes["publishingComplete"] = data["publishing_complete"]
    ctx.company.notification_settings_json = notes
    await db.commit()
    await db.refresh(ctx.company)
    return _ok(serialize.company_out(ctx.company, owner=ctx.user))

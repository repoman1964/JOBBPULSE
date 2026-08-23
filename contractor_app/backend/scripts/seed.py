"""Seed Johnson Outdoor Living demo data (build doc §19)."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select

from app.db.session import AsyncSessionLocal, engine
from app.integrations.storage.s3 import ObjectStorage
from app.models import (
    Company,
    ContentPackage,
    Contractor,
    GeneratedAsset,
    GeneratedAssetVersion,
    Job,
    MediaAsset,
    SocialConnection,
    SocialProfile,
)
from app.models.company import (
    DEFAULT_NOTIFICATION_SETTINGS,
    DEFAULT_PHOTO_MAXIMUMS,
    DEFAULT_PHOTO_MINIMUMS,
)
from app.models.enums import (
    AssetStatus,
    InternalJobStatus,
    MediaKind,
    PackageStatus,
    PublicJobStatus,
    SocialConnectionStatus,
    UploadStatus,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

COMPANY_ID = UUID("11111111-1111-1111-1111-111111111111")
CONTRACTOR_ID = UUID("22222222-2222-2222-2222-222222222222")
JOB_DECK = UUID("33333333-3333-3333-3333-333333333301")
JOB_KITCHEN = UUID("33333333-3333-3333-3333-333333333302")
JOB_PAINT = UUID("33333333-3333-3333-3333-333333333303")


def _placeholder_jpeg(seed: str) -> bytes:
    # Minimal valid-ish JPEG header + padding (enough for MinIO object)
    # Real images can replace later; API only needs object presence.
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + seed.encode()
        + b"\x00" * 64
        + b"\xff\xd9"
    )


async def seed() -> None:
    storage = ObjectStorage()
    try:
        storage.ensure_bucket()
    except Exception as exc:
        logger.warning("MinIO ensure_bucket failed (continuing): %s", exc)

    async with AsyncSessionLocal() as session:
        existing = await session.get(Company, COMPANY_ID)
        if existing:
            logger.info("Seed company already exists — skipping full reseed.")
            await session.commit()
            return

        company = Company(
            id=COMPANY_ID,
            name="Johnson Outdoor Living",
            slug="johnson-outdoor-living",
            contact_name="Mike Johnson",
            phone="(404) 555-0142",
            email="mike@johnsonoutdoor.example",
            website="https://johnsonoutdoor.example",
            service_area="Metro Atlanta",
            photo_minimums_json=dict(DEFAULT_PHOTO_MINIMUMS),
            photo_maximums_json=dict(DEFAULT_PHOTO_MAXIMUMS),
            notification_settings_json=dict(DEFAULT_NOTIFICATION_SETTINGS),
        )
        contractor = Contractor(
            id=CONTRACTOR_ID,
            company_id=COMPANY_ID,
            name="Mike Johnson",
            email="mike@johnsonoutdoor.example",
            phone="(404) 555-0142",
            role="owner",
            status="active",
        )
        session.add(company)
        session.add(contractor)

        now = datetime.now(UTC)
        jobs = [
            Job(
                id=JOB_DECK,
                company_id=COMPANY_ID,
                created_by_contractor_id=CONTRACTOR_ID,
                name="Johnson Deck Rebuild",
                service_type="Deck rebuild",
                city="Marietta",
                region="GA",
                location_text="Marietta, GA",
                public_status=PublicJobStatus.active.value,
                internal_status=InternalJobStatus.draft.value,
                created_at=now - timedelta(days=3),
            ),
            Job(
                id=JOB_KITCHEN,
                company_id=COMPANY_ID,
                created_by_contractor_id=CONTRACTOR_ID,
                name="Miller Kitchen Cabinets",
                service_type="Cabinets",
                city="Roswell",
                region="GA",
                location_text="Roswell, GA",
                public_status=PublicJobStatus.active.value,
                internal_status=InternalJobStatus.draft.value,
                created_at=now - timedelta(days=5),
            ),
            Job(
                id=JOB_PAINT,
                company_id=COMPANY_ID,
                created_by_contractor_id=CONTRACTOR_ID,
                name="Thompson Exterior Painting",
                service_type="Exterior painting",
                city="Decatur",
                region="GA",
                location_text="Decatur, GA",
                public_status=PublicJobStatus.ready_for_approval.value,
                internal_status=InternalJobStatus.ready_for_approval.value,
                submission_version=1,
                submitted_at=now - timedelta(days=1),
                created_at=now - timedelta(days=10),
            ),
        ]
        for j in jobs:
            session.add(j)

        def add_photos(job_id: UUID, category: str, count: int, prefix: str) -> list[MediaAsset]:
            items: list[MediaAsset] = []
            for i in range(1, count + 1):
                mid = uuid4()
                key = f"companies/{COMPANY_ID}/jobs/{job_id}/photos/{mid}"
                try:
                    storage.put_bytes(key, _placeholder_jpeg(f"{prefix}-{i}"), "image/jpeg")
                except Exception as exc:
                    logger.warning("put photo failed: %s", exc)
                m = MediaAsset(
                    id=mid,
                    company_id=COMPANY_ID,
                    job_id=job_id,
                    uploaded_by_contractor_id=CONTRACTOR_ID,
                    kind=MediaKind.photo.value,
                    photo_category=category,
                    original_object_key=key,
                    preview_object_key=key,
                    thumbnail_object_key=key,
                    mime_type="image/jpeg",
                    byte_size=240_000,
                    upload_status=UploadStatus.complete.value,
                    is_favorite=(i == 1 and category == "before"),
                    version=1,
                )
                session.add(m)
                items.append(m)
            return items

        deck_before = add_photos(JOB_DECK, "before", 4, "deck-b")
        add_photos(JOB_DECK, "progress", 7, "deck-p")
        add_photos(JOB_KITCHEN, "before", 5, "kit-b")
        add_photos(JOB_KITCHEN, "progress", 3, "kit-p")
        paint_before = add_photos(JOB_PAINT, "before", 6, "paint-b")
        add_photos(JOB_PAINT, "progress", 4, "paint-p")
        paint_after = add_photos(JOB_PAINT, "after", 8, "paint-a")

        # Voice for paint job
        voice_id = uuid4()
        voice_key = f"companies/{COMPANY_ID}/jobs/{JOB_PAINT}/voice/{voice_id}"
        try:
            storage.put_bytes(voice_key, b"FAKEAUDIO", "audio/webm")
        except Exception:
            pass
        session.add(
            MediaAsset(
                id=voice_id,
                company_id=COMPANY_ID,
                job_id=JOB_PAINT,
                uploaded_by_contractor_id=CONTRACTOR_ID,
                kind=MediaKind.audio.value,
                original_object_key=voice_key,
                preview_object_key=voice_key,
                mime_type="audio/webm",
                byte_size=12000,
                duration_ms=45000,
                upload_status=UploadStatus.complete.value,
                is_active_voice=True,
                version=1,
            )
        )
        # Persist media before packages reference featured media FKs
        await session.flush()

        # Package ready for approval
        package_id = uuid4()
        fb = paint_before[0].id if paint_before else None
        fa = paint_after[0].id if paint_after else None
        package = ContentPackage(
            id=package_id,
            company_id=COMPANY_ID,
            job_id=JOB_PAINT,
            version=1,
            status=PackageStatus.ready_for_approval.value,
            project_description=(
                "We completed Thompson Exterior Painting in Decatur, GA. "
                "The crew documented the full transformation from start to finish."
            ),
            featured_before_media_id=fb,
            featured_after_media_id=fa,
        )
        session.add(package)
        await session.flush()

        for dest, title, body in [
            ("facebook", "Facebook", "Thompson Exterior Painting: another transformation ready to share."),
            ("instagram", "Instagram", "Thompson Exterior Painting complete in Decatur. #JobbPulse"),
            (
                "google_business",
                "Google Business Profile",
                "Just finished Thompson Exterior Painting in Decatur. "
                "Solid prep, a clean finish, and a crew that shows up ready to work. "
                "Call us if you have a similar project.",
            ),
            ("conversion_site", "Project Page", package.project_description),
            ("portfolio_site", "JobbPulse Portfolio", package.project_description),
        ]:
            asset_id = uuid4()
            asset = GeneratedAsset(
                id=asset_id,
                company_id=COMPANY_ID,
                package_id=package_id,
                destination_type=dest,
                title=title,
                body=body,
                payload_json={"destination": dest},
                preview_json={},
                status=AssetStatus.ready.value,
            )
            session.add(asset)
            await session.flush()
            version_id = uuid4()
            version = GeneratedAssetVersion(
                id=version_id,
                generated_asset_id=asset_id,
                version=1,
                source_media_ids_json=[str(x) for x in [fb, fa] if x],
                title=title,
                body=body,
                payload_json={"destination": dest},
                preview_json={},
                generation_metadata_json={"seed": True},
            )
            session.add(version)
            await session.flush()
            asset.active_version_id = version_id

        # Social profile + mixed connections
        profile = SocialProfile(
            company_id=COMPANY_ID,
            provider="upload_post",
            provider_username=f"jp_{str(COMPANY_ID).replace('-', '')[:24]}",
            status="active",
        )
        session.add(profile)
        await session.flush()
        for platform, status, name in [
            ("facebook", SocialConnectionStatus.connected.value, "Johnson Outdoor Living"),
            ("instagram", SocialConnectionStatus.connected.value, "@johnsonoutdoor"),
            ("google_business", SocialConnectionStatus.not_connected.value, None),
            ("tiktok", SocialConnectionStatus.not_connected.value, None),
            ("youtube", SocialConnectionStatus.not_connected.value, None),
        ]:
            session.add(
                SocialConnection(
                    company_id=COMPANY_ID,
                    social_profile_id=profile.id,
                    platform=platform,
                    status=status,
                    provider_account_name=name,
                    reason="Reconnect required" if status == "reconnect_required" else None,
                )
            )

        await session.commit()
        logger.info("Seed complete: Johnson Outdoor Living / mike@johnsonoutdoor.example")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()

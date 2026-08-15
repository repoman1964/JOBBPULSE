#!/usr/bin/env python3
"""Force-seed Red Clay Cabinet Installers as a full product-demo contractor.

Creates (or replaces) the Red Clay company with:
  - Owner login: owner+red-clay-cabinet-installers@demo.jobpulse.local / password123
  - 6 published jobs with real before/after JPEGs (MinIO)
  - Directory listings (feeds public API + red_clay_website + portfolio_website)
  - Mock Facebook + Instagram connections
  - Mock social + directory publication rows (as if published from the contractor app)

Usage:
  cd api && PYTHONPATH=. .venv/bin/python scripts/seed_red_clay_demo.py
  # or from monorepo root: make red-clay-seed
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, select, text

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.core.security import hash_password
from app.core.slug import slugify
from app.core import storage as storage_svc
from app.db.models import (
    Company,
    CompanyMembership,
    CompanyService,
    CompanyServiceArea,
    ContentVariant,
    ContentType,
    ContentVariantStatus,
    ContractorProfile,
    DirectoryListing,
    DirectoryListingMedia,
    DirectoryListingStatus,
    GenerationRun,
    GenerationRunStatus,
    GenerationType,
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipRole,
    MembershipStatus,
    PublicationDestinationType,
    PublicationJob,
    PublicationJobStatus,
    PublishingConnection,
    PublishingConnectionStatus,
    User,
)
from app.db.session import AsyncSessionLocal

MEDIA_DIR = Path(__file__).resolve().parent / "demo_media" / "red-clay"
SLUG = "red-clay-cabinet-installers"
OWNER_EMAIL = f"owner+{SLUG}@demo.jobpulse.local"
OWNER_PASSWORD = "password123"

PROJECTS = [
    {
        "key": "buckhead-kitchen",
        "private_title": "Chen / Buckhead kitchen",
        "title": "Kitchen Cabinet Install in Buckhead",
        "summary": (
            "Full kitchen cabinet install in Buckhead: removed the old boxes, leveled "
            "everything, and hung white shaker uppers and lowers with soft-close. Floors "
            "protected throughout; finished in three days with a two-person crew."
        ),
        "social": (
            "Just wrapped a full white-shaker kitchen in Buckhead 🔧 Soft-close hardware, "
            "clean lines, floors protected the whole way. Another metro Atlanta home "
            "looking sharp. #AtlantaKitchen #CabinetInstall #RedClayCabinets"
        ),
        "service_key": "kitchen_cabinets",
        "city": "Atlanta",
        "state": "GA",
        "location_display": "Buckhead, Atlanta, GA",
        "featured": True,
        "days_ago": 4,
        "before": "buckhead-kitchen-before.jpg",
        "after": "buckhead-kitchen-after.jpg",
    },
    {
        "key": "inman-vanity",
        "private_title": "Lopez / Inman Park vanity",
        "title": "Double Vanity Install in Inman Park",
        "summary": (
            "Swapped a worn oak double vanity for a fresh white unit in Inman Park. "
            "Plumbed, leveled, and caulked; left the bath spotless for the homeowners."
        ),
        "social": (
            "Inman Park bath upgrade complete — new double vanity, soft-close drawers, "
            "clean reconnect. Small room, big difference. #BathRemodel #AtlantaHomes"
        ),
        "service_key": "bathroom_vanity",
        "city": "Atlanta",
        "state": "GA",
        "location_display": "Inman Park, Atlanta, GA",
        "featured": False,
        "days_ago": 11,
        "before": "inman-vanity-before.jpg",
        "after": "inman-vanity-after.jpg",
    },
    {
        "key": "decatur-pantry",
        "private_title": "Patel / Decatur pantry",
        "title": "Custom Pantry Built-In in Decatur",
        "summary": (
            "Floor-to-ceiling pantry built-in with adjustable shelves in Decatur. "
            "Client can finally see their dry goods and stop the hallway clutter."
        ),
        "social": (
            "Wire shelves → custom pantry in Decatur. Adjustable shelves, glass doors, "
            "and room for the real grocery haul. #BuiltIns #DecaturGA #PantryGoals"
        ),
        "service_key": "pantry_built_ins",
        "city": "Decatur",
        "state": "GA",
        "location_display": "Decatur, GA",
        "featured": True,
        "days_ago": 18,
        "before": "decatur-pantry-before.jpg",
        "after": "decatur-pantry-after.jpg",
    },
    {
        "key": "marietta-kitchen",
        "private_title": "Nguyen / Marietta kitchen",
        "title": "Soft-Close Kitchen Refresh in Marietta",
        "summary": (
            "Kitchen cabinet refresh in Marietta: sage green shaker set, soft-close "
            "hardware, and careful fit around stainless appliances for a quieter finish."
        ),
        "social": (
            "Marietta kitchen refresh — sage shaker, soft-close everywhere, clean install. "
            "From honey oak to something the whole family smiles about. #KitchenRefresh"
        ),
        "service_key": "kitchen_cabinets",
        "city": "Marietta",
        "state": "GA",
        "location_display": "Marietta, GA",
        "featured": False,
        "days_ago": 27,
        "before": "marietta-kitchen-before.jpg",
        "after": "marietta-kitchen-after.jpg",
    },
    {
        "key": "sandy-springs-laundry",
        "private_title": "Brooks / Sandy Springs laundry",
        "title": "Laundry Cabinet Install in Sandy Springs",
        "summary": (
            "Utility-room cabinet install in Sandy Springs: uppers, lowers, folding "
            "counter, and storage for the mess that used to live on wire shelves."
        ),
        "social": (
            "Sandy Springs laundry glow-up. Cabinets + folding space where wire shelves "
            "used to lose the war. #LaundryRoom #CabinetInstall #MetroAtlanta"
        ),
        "service_key": "cabinet_installation",
        "city": "Sandy Springs",
        "state": "GA",
        "location_display": "Sandy Springs, GA",
        "featured": False,
        "days_ago": 35,
        "before": "sandy-springs-laundry-before.jpg",
        "after": "sandy-springs-laundry-after.jpg",
    },
    {
        "key": "roswell-island",
        "private_title": "Kim / Roswell island kitchen",
        "title": "Kitchen Island & Cabinets in Roswell",
        "summary": (
            "Full kitchen cabinet install in Roswell with white perimeter cabinets and "
            "a walnut island—soft-close drawers, quartz tops, clean appliance panels."
        ),
        "social": (
            "Roswell kitchen: white perimeters + walnut island. Soft-close, quartz, "
            "and a layout built for real cooking. Before/after on the site. #RoswellGA"
        ),
        "service_key": "kitchen_cabinets",
        "city": "Roswell",
        "state": "GA",
        "location_display": "Roswell, GA",
        "featured": True,
        "days_ago": 9,
        "before": "roswell-island-before.jpg",
        "after": "roswell-island-after.jpg",
    },
]

SERVICES = [
    ("kitchen_cabinets", "Kitchen Cabinets"),
    ("bathroom_vanity", "Bath Vanities"),
    ("pantry_built_ins", "Pantries & Built-ins"),
    ("cabinet_installation", "Cabinet Installation"),
]

AREAS = [
    ("Atlanta", "GA", True),
    ("Decatur", "GA", False),
    ("Marietta", "GA", False),
    ("Roswell", "GA", False),
    ("Sandy Springs", "GA", False),
]


def _load_jpeg(name: str) -> bytes:
    path = MEDIA_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing demo media: {path}")
    return path.read_bytes()


async def _upload_jpeg(key: str, data: bytes) -> None:
    try:
        storage_svc.ensure_bucket()
        storage_svc.put_bytes(key, data, "image/jpeg")
    except Exception as exc:  # noqa: BLE001
        print(f"  warning: media upload skipped for {key}: {exc}")


async def _purge_red_clay(db) -> None:
    """Remove existing Red Clay company + owner via SQL so ORM cascades don't null FKs."""
    result = await db.execute(select(Company.id).where(Company.slug == SLUG))
    company_id = result.scalar_one_or_none()
    if company_id is not None:
        # Explicit dependency order; company-level CASCADE covers most child tables.
        await db.execute(
            text(
                """
                DELETE FROM publication_jobs
                WHERE job_id IN (SELECT id FROM jobs WHERE company_id = :cid)
                """
            ),
            {"cid": company_id},
        )
        await db.execute(
            text(
                """
                DELETE FROM directory_listing_media
                WHERE directory_listing_id IN (
                    SELECT id FROM directory_listings WHERE company_id = :cid
                )
                """
            ),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM directory_listings WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM directory_leads WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM contractor_profiles WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(
            text(
                """
                DELETE FROM content_variants
                WHERE job_id IN (SELECT id FROM jobs WHERE company_id = :cid)
                """
            ),
            {"cid": company_id},
        )
        await db.execute(
            text(
                """
                DELETE FROM generation_runs
                WHERE job_id IN (SELECT id FROM jobs WHERE company_id = :cid)
                """
            ),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM media_assets WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(text("DELETE FROM jobs WHERE company_id = :cid"), {"cid": company_id})
        await db.execute(
            text("DELETE FROM publishing_connections WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM company_memberships WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM company_services WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(
            text("DELETE FROM company_service_areas WHERE company_id = :cid"),
            {"cid": company_id},
        )
        await db.execute(text("DELETE FROM companies WHERE id = :cid"), {"cid": company_id})
        await db.flush()
        print(f"removed existing company {SLUG}")

    user_result = await db.execute(select(User).where(User.email == OWNER_EMAIL))
    user = user_result.scalar_one_or_none()
    if user is not None:
        await db.execute(delete(User).where(User.id == user.id))
        await db.flush()
        print(f"removed owner {OWNER_EMAIL}")


async def seed() -> None:
    missing = [
        p[k]
        for p in PROJECTS
        for k in ("before", "after")
        if not (MEDIA_DIR / p[k]).is_file()
    ]
    if missing:
        raise SystemExit(f"Missing media files under {MEDIA_DIR}: {missing}")

    async with AsyncSessionLocal() as db:
        await _purge_red_clay(db)

        user = User(
            email=OWNER_EMAIL,
            full_name="Jordan Hale",
            password_hash=hash_password(OWNER_PASSWORD),
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        await db.flush()

        company = Company(
            name="Red Clay Cabinet Installers",
            slug=SLUG,
            trade="cabinet_installation",
            description=(
                "Red Clay Cabinet Installers puts in kitchen cabinets, bath vanities, and custom "
                "built-ins for homeowners across metro Atlanta. We measure carefully, protect your "
                "floors, and leave the jobsite clean. Whether it’s a full kitchen remodel in Buckhead "
                "or a vanity upgrade in Decatur, every project is real work from real homes—not "
                "catalog renders."
            ),
            phone="404-555-0148",
            website_url="http://localhost:3002",
            onboarding_completed=True,
            is_active=True,
            default_tone="friendly_local",
            default_call_to_action="Call for a free estimate",
            subscription_status="active",
            subscription_plan="core",
        )
        db.add(company)
        await db.flush()

        db.add(
            CompanyMembership(
                company_id=company.id,
                user_id=user.id,
                role=MembershipRole.owner,
                status=MembershipStatus.active,
            )
        )

        for key, display in SERVICES:
            db.add(
                CompanyService(
                    company_id=company.id,
                    service_key=key,
                    display_name=display,
                    is_active=True,
                )
            )
        for city, state, primary in AREAS:
            db.add(
                CompanyServiceArea(
                    company_id=company.id,
                    city=city,
                    state=state,
                    display_name=f"{city}, {state}",
                    is_primary=primary,
                )
            )

        profile = ContractorProfile(
            company_id=company.id,
            public_slug=SLUG,
            headline="Kitchen cabinets, vanities, and built-ins—installed clean across metro Atlanta.",
            public_description=company.description,
            contact_phone=company.phone,
            website_url=company.website_url,
            lead_form_enabled=True,
            published=True,
            featured=True,
            seo_title="Red Clay Cabinet Installers | JobPulse",
            seo_description=(company.description or "")[:500],
        )
        db.add(profile)
        await db.flush()

        # Mock social accounts (as if connected in contractor Account screen)
        now = datetime.now(timezone.utc)
        fb = PublishingConnection(
            company_id=company.id,
            provider="mock",
            platform="facebook",
            external_account_id="mock-fb-red-clay",
            display_name="Red Clay Cabinet Installers",
            status=PublishingConnectionStatus.active,
            last_verified_at=now,
        )
        ig = PublishingConnection(
            company_id=company.id,
            provider="mock",
            platform="instagram",
            external_account_id="mock-ig-red-clay",
            display_name="@redclaycabinets",
            status=PublishingConnectionStatus.active,
            last_verified_at=now,
        )
        db.add_all([fb, ig])
        await db.flush()

        created = 0
        for project in PROJECTS:
            published_at = now - timedelta(days=project["days_ago"])
            job = Job(
                company_id=company.id,
                created_by=user.id,
                title=project["private_title"],
                service_key=project["service_key"],
                location_display=project["location_display"],
                city=project["city"],
                state=project["state"],
                status=JobStatus.published,
                published_at=published_at,
            )
            db.add(job)
            await db.flush()

            # Mock generation run + social/directory variants (approved)
            gen = GenerationRun(
                job_id=job.id,
                requested_by=user.id,
                generation_type=GenerationType.initial,
                status=GenerationRunStatus.completed,
                model_provider="mock",
                model_name="mock-v1",
                completed_at=published_at - timedelta(hours=3),
            )
            db.add(gen)
            await db.flush()

            social_variant = ContentVariant(
                job_id=job.id,
                generation_run_id=gen.id,
                content_type=ContentType.primary_social,
                status=ContentVariantStatus.approved,
                title=project["title"],
                body_generated=project["social"],
                body_edited=project["social"],
                version_number=1,
                approved_at=published_at - timedelta(hours=2),
                approved_by=user.id,
            )
            directory_variant = ContentVariant(
                job_id=job.id,
                generation_run_id=gen.id,
                content_type=ContentType.directory_listing,
                status=ContentVariantStatus.approved,
                title=project["title"],
                body_generated=project["summary"],
                body_edited=project["summary"],
                version_number=1,
                approved_at=published_at - timedelta(hours=2),
                approved_by=user.id,
            )
            db.add_all([social_variant, directory_variant])
            await db.flush()

            service_slug = slugify(project["service_key"])[:40]
            city_slug = slugify(project["city"])[:40]
            listing_slug = f"{service_slug}-{city_slug}-{project['key']}"
            listing = DirectoryListing(
                job_id=job.id,
                company_id=company.id,
                contractor_profile_id=profile.id,
                slug=listing_slug,
                public_title=project["title"],
                public_summary=project["summary"],
                service_key=project["service_key"],
                location_display=project["location_display"],
                city=project["city"],
                state=project["state"],
                status=DirectoryListingStatus.published,
                published_at=published_at,
                featured=bool(project.get("featured")),
                seo_title=f"{project['title']} | Red Clay"[:300],
                seo_description=project["summary"][:500],
            )
            db.add(listing)
            await db.flush()

            # Before (order 0) then after (order 1, primary for cards)
            for order, (stage, filename) in enumerate(
                [
                    (MediaStageLabel.before, project["before"]),
                    (MediaStageLabel.after, project["after"]),
                ]
            ):
                blob = _load_jpeg(filename)
                key = f"seed/{SLUG}/{listing_slug}/{stage.value}.jpg"
                await _upload_jpeg(key, blob)
                asset = MediaAsset(
                    company_id=company.id,
                    job_id=job.id,
                    uploaded_by=user.id,
                    asset_type=MediaAssetType.image,
                    stage_label=stage,
                    storage_key=key,
                    original_filename=filename,
                    mime_type="image/jpeg",
                    file_size_bytes=len(blob),
                    processing_status=MediaProcessingStatus.ready,
                    width=1152,
                    height=864,
                    is_primary=(stage == MediaStageLabel.after),
                )
                db.add(asset)
                await db.flush()
                db.add(
                    DirectoryListingMedia(
                        directory_listing_id=listing.id,
                        media_asset_id=asset.id,
                        stage_label=stage.value,
                        display_order=order,
                    )
                )

            # Directory publication
            db.add(
                PublicationJob(
                    job_id=job.id,
                    content_variant_id=directory_variant.id,
                    destination_type=PublicationDestinationType.directory,
                    provider="first_party",
                    status=PublicationJobStatus.published,
                    idempotency_key=f"seed-dir-{job.id}",
                    external_url=f"http://localhost:3001/projects/{listing_slug}",
                    attempt_count=1,
                    published_at=published_at,
                )
            )
            # Facebook + Instagram mock posts
            for conn, platform_label in ((fb, "facebook"), (ig, "instagram")):
                db.add(
                    PublicationJob(
                        job_id=job.id,
                        content_variant_id=social_variant.id,
                        destination_type=PublicationDestinationType.social,
                        publishing_connection_id=conn.id,
                        provider="mock",
                        status=PublicationJobStatus.published,
                        idempotency_key=f"seed-{platform_label}-{job.id}",
                        external_url=f"https://mock.social/{platform_label}/red-clay/{project['key']}",
                        provider_response_json={
                            "platform": platform_label,
                            "caption": project["social"][:200],
                            "mock": True,
                        },
                        attempt_count=1,
                        published_at=published_at + timedelta(minutes=5),
                    )
                )

            created += 1
            print(f"  + project {listing_slug}")

        await db.commit()
        print()
        print(f"Red Clay demo ready: {created} projects published to directory + mock social.")
        print(f"  Contractor slug: {SLUG}")
        print(f"  Owner login:     {OWNER_EMAIL}")
        print(f"  Password:        {OWNER_PASSWORD}")
        print("  Website:         http://localhost:3002 (red_clay_website)")
        print("  Directory:       http://localhost:3001/contractors/red-clay-cabinet-installers")
        print("  API public:      http://localhost:8000/api/v1/public/projects?contractor_slug=red-clay-cabinet-installers")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()

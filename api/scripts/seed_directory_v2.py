#!/usr/bin/env python3
"""Seed Georgia-metro demo contractors and published directory projects.

Usage (from repo root or api/):
  cd api && PYTHONPATH=. .venv/bin/python scripts/seed_directory_v2.py

Idempotent on company slug: re-running skips contractors that already exist.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure api package root is importable
API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import select

from app.core.security import hash_password
from app.core.slug import slugify
from app.core import storage as storage_svc
from app.db.models import (
    Company,
    CompanyMembership,
    CompanyService,
    CompanyServiceArea,
    ContractorProfile,
    DirectoryListing,
    DirectoryListingMedia,
    DirectoryListingStatus,
    Job,
    JobStatus,
    MediaAsset,
    MediaAssetType,
    MediaProcessingStatus,
    MediaStageLabel,
    MembershipRole,
    MembershipStatus,
    User,
)
from app.db.session import AsyncSessionLocal

# Minimal 1x1 PNGs with different colors via tiny valid PNG payloads
PNG_AFTER = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)
PNG_BEFORE = PNG_AFTER  # same bytes; stage labels differentiate

CONTRACTORS = [
    {
        "name": "Smith Painting",
        "slug": "smith-painting-demo",
        "trade": "painting",
        "phone": "770-555-0101",
        "headline": "Precision painting for North Atlanta homes",
        "description": (
            "Family-owned painting company documenting completed exterior and "
            "interior projects across Cobb and Fulton counties."
        ),
        "services": [
            ("exterior_paint", "Exterior Painting"),
            ("interior_painting", "Interior Painting"),
            ("painting", "Painting"),
        ],
        "areas": [
            ("Marietta", "GA", True),
            ("Roswell", "GA", False),
            ("East Cobb", "GA", False),
        ],
        "featured": True,
        "projects": [
            {
                "title": "Exterior House Painting in Marietta",
                "summary": (
                    "Full exterior repaint on a two-story home in Marietta. "
                    "Prep included scraping, caulk, and primer before two coats of premium exterior acrylic."
                ),
                "service_key": "exterior_paint",
                "city": "Marietta",
                "state": "GA",
                "location_display": "Marietta, GA",
                "featured": True,
                "days_ago": 12,
            },
            {
                "title": "Interior Repainting Project in Roswell",
                "summary": (
                    "Whole-home interior repaint with accent walls in the living room. "
                    "Low-VOC paint selected for family-friendly rooms."
                ),
                "service_key": "interior_painting",
                "city": "Roswell",
                "state": "GA",
                "location_display": "Roswell, GA",
                "featured": False,
                "days_ago": 28,
            },
            {
                "title": "Front Door and Trim Refresh in East Cobb",
                "summary": (
                    "High-visibility front elevation refresh: door, shutters, and trim "
                    "repainted for curb appeal before listing."
                ),
                "service_key": "painting",
                "city": "Marietta",
                "state": "GA",
                "location_display": "East Cobb, Marietta, GA",
                "featured": False,
                "days_ago": 45,
            },
        ],
    },
    {
        "name": "Metro Tree Pros",
        "slug": "metro-tree-pros-demo",
        "trade": "tree_service",
        "phone": "404-555-0202",
        "headline": "Safe tree removal and stump grinding",
        "description": (
            "ISA-trained crews documenting complex removals and routine pruning "
            "around Atlanta metro properties."
        ),
        "services": [
            ("tree_removal", "Tree Removal"),
            ("tree_service", "Tree Service"),
            ("stump_removal", "Stump Removal"),
        ],
        "areas": [
            ("Decatur", "GA", True),
            ("Atlanta", "GA", False),
            ("Smyrna", "GA", False),
        ],
        "featured": True,
        "projects": [
            {
                "title": "Large Oak Tree Removal in Decatur",
                "summary": (
                    "Sectional removal of a storm-damaged oak near the home. "
                    "Crew protected the roof and driveway throughout the drop."
                ),
                "service_key": "tree_removal",
                "city": "Decatur",
                "state": "GA",
                "location_display": "Decatur, GA",
                "featured": True,
                "days_ago": 8,
            },
            {
                "title": "Stump Removal After Storm Cleanup in Atlanta",
                "summary": (
                    "Grinded three stumps flush and cleaned chips so the yard could be reseeded."
                ),
                "service_key": "stump_removal",
                "city": "Atlanta",
                "state": "GA",
                "location_display": "Atlanta, GA",
                "featured": False,
                "days_ago": 21,
            },
            {
                "title": "Backyard Tree Pruning in Smyrna",
                "summary": (
                    "Selective pruning to open canopy and clear roof lines on a residential lot."
                ),
                "service_key": "tree_service",
                "city": "Smyrna",
                "state": "GA",
                "location_display": "Smyrna, GA",
                "featured": False,
                "days_ago": 35,
            },
        ],
    },
    {
        "name": "Peach Hardscapes",
        "slug": "peach-hardscapes-demo",
        "trade": "hardscaping",
        "phone": "678-555-0303",
        "headline": "Patios and outdoor living built to last",
        "description": (
            "Hardscape specialists creating paver patios, retaining walls, and "
            "walkways across north metro Atlanta."
        ),
        "services": [
            ("hardscaping", "Hardscaping"),
            ("paver_patio", "Paver Patio"),
            ("landscape_installation", "Landscape Installation"),
        ],
        "areas": [
            ("Alpharetta", "GA", True),
            ("Johns Creek", "GA", False),
            ("Roswell", "GA", False),
        ],
        "featured": False,
        "projects": [
            {
                "title": "Backyard Paver Patio Installation in Alpharetta",
                "summary": (
                    "Installed a 400 sq ft paver patio with seating wall. "
                    "Base prep and polymeric sand for long-term stability."
                ),
                "service_key": "paver_patio",
                "city": "Alpharetta",
                "state": "GA",
                "location_display": "Alpharetta, GA",
                "featured": True,
                "days_ago": 5,
            },
            {
                "title": "Retaining Wall and Steps in Johns Creek",
                "summary": (
                    "Block retaining wall with integrated steps to reclaim a sloped backyard."
                ),
                "service_key": "hardscaping",
                "city": "Johns Creek",
                "state": "GA",
                "location_display": "Johns Creek, GA",
                "featured": False,
                "days_ago": 40,
            },
            {
                "title": "Front Walkway Landscape Install in Roswell",
                "summary": (
                    "New walkway pavers and bed edging with fresh plantings for the front elevation."
                ),
                "service_key": "landscape_installation",
                "city": "Roswell",
                "state": "GA",
                "location_display": "Roswell, GA",
                "featured": False,
                "days_ago": 55,
            },
        ],
    },
    {
        "name": "FenceLine Atlanta",
        "slug": "fenceline-atlanta-demo",
        "trade": "fencing",
        "phone": "470-555-0404",
        "headline": "Wood and privacy fencing done right",
        "description": "Residential fence installs with clear before-and-after documentation.",
        "services": [
            ("fencing", "Fencing"),
            ("deck_building", "Deck Building"),
        ],
        "areas": [
            ("Smyrna", "GA", True),
            ("Marietta", "GA", False),
            ("Atlanta", "GA", False),
        ],
        "featured": False,
        "projects": [
            {
                "title": "Privacy Fence Installation in Smyrna",
                "summary": (
                    "Six-foot wood privacy fence along three property lines with a double gate."
                ),
                "service_key": "fencing",
                "city": "Smyrna",
                "state": "GA",
                "location_display": "Smyrna, GA",
                "featured": False,
                "days_ago": 18,
            },
            {
                "title": "Back Deck Rebuild in Marietta",
                "summary": (
                    "Replaced aging deck boards and rails with composite decking for low maintenance."
                ),
                "service_key": "deck_building",
                "city": "Marietta",
                "state": "GA",
                "location_display": "Marietta, GA",
                "featured": False,
                "days_ago": 60,
            },
        ],
    },
]


async def _upload_image(key: str, data: bytes) -> None:
    try:
        storage_svc.ensure_bucket()
        storage_svc.put_bytes(key, data, "image/png")
    except Exception as exc:  # noqa: BLE001
        print(f"  warning: media upload skipped for {key}: {exc}")


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        created_contractors = 0
        created_projects = 0

        for spec in CONTRACTORS:
            existing = await db.execute(select(Company).where(Company.slug == spec["slug"]))
            if existing.scalar_one_or_none() is not None:
                print(f"skip company {spec['slug']} (already exists)")
                continue

            email = f"owner+{spec['slug']}@demo.jobpulse.local"
            user = User(
                email=email,
                full_name=f"{spec['name']} Owner",
                password_hash=hash_password("password123"),
                is_verified=True,
                is_active=True,
            )
            db.add(user)
            await db.flush()

            company = Company(
                name=spec["name"],
                slug=spec["slug"],
                trade=spec["trade"],
                description=spec["description"],
                phone=spec["phone"],
                website_url=f"https://example.com/{spec['slug']}",
                onboarding_completed=True,
                is_active=True,
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

            for key, display in spec["services"]:
                db.add(
                    CompanyService(
                        company_id=company.id,
                        service_key=key,
                        display_name=display,
                        is_active=True,
                    )
                )
            for city, state, primary in spec["areas"]:
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
                public_slug=spec["slug"],
                headline=spec["headline"],
                public_description=spec["description"],
                contact_phone=spec["phone"],
                website_url=company.website_url,
                lead_form_enabled=True,
                published=True,
                featured=bool(spec.get("featured")),
                seo_title=f"{spec['name']} | JobPulse",
                seo_description=spec["description"][:500],
            )
            db.add(profile)
            await db.flush()
            created_contractors += 1

            for project in spec["projects"]:
                job = Job(
                    company_id=company.id,
                    created_by=user.id,
                    title=f"PRIVATE {project['title']}",
                    service_key=project["service_key"],
                    location_display=project["location_display"],
                    city=project["city"],
                    state=project["state"],
                    status=JobStatus.published,
                    published_at=datetime.now(timezone.utc) - timedelta(days=project["days_ago"]),
                )
                db.add(job)
                await db.flush()

                service_slug = slugify(project["service_key"])[:40]
                city_slug = slugify(project["city"])[:40]
                listing_slug = f"{service_slug}-{city_slug}-{job.id.hex[:8]}"
                published_at = datetime.now(timezone.utc) - timedelta(days=project["days_ago"])
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
                    seo_title=f"{project['title']} | JobPulse"[:300],
                    seo_description=project["summary"][:500],
                )
                db.add(listing)
                await db.flush()

                # Media assets
                for order, (stage, blob) in enumerate(
                    [
                        (MediaStageLabel.after, PNG_AFTER),
                        (MediaStageLabel.before, PNG_BEFORE),
                    ]
                ):
                    key = f"demo/{spec['slug']}/{listing_slug}/{stage.value}-{order}.png"
                    await _upload_image(key, blob)
                    asset = MediaAsset(
                        company_id=company.id,
                        job_id=job.id,
                        uploaded_by=user.id,
                        asset_type=MediaAssetType.image,
                        stage_label=stage,
                        storage_key=key,
                        original_filename=f"{stage.value}.png",
                        mime_type="image/png",
                        file_size_bytes=len(blob),
                        processing_status=MediaProcessingStatus.ready,
                        width=1,
                        height=1,
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
                created_projects += 1
                print(f"  + project {listing_slug}")

            print(f"created contractor {spec['name']} ({spec['slug']})")

        await db.commit()
        print(f"done: {created_contractors} contractors, {created_projects} projects")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()

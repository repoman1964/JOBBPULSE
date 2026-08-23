"""Public demo project list/detail used by Red Clay."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.slug import public_project_slug
from app.services.public_demo import ELIGIBLE_PUBLIC_STATUSES, serialize_demo_list_item


def test_public_project_slug_is_stable_kebab_plus_job_prefix() -> None:
    job_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    slug = public_project_slug("Exterior painting in Decatur", job_id)
    assert slug == "exterior-painting-in-decatur-a1b2"
    assert public_project_slug("Exterior painting in Decatur", job_id) == slug


def test_public_list_without_email_returns_422(client: TestClient) -> None:
    resp = client.get("/api/v1/public/demo/projects")
    assert resp.status_code == 422


def test_public_list_unknown_email_returns_empty(client: TestClient) -> None:
    resp = client.get(
        "/api/v1/public/demo/projects",
        params={"email": "nobody@example.com"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"items": []}


def test_list_item_serializer_omits_private_job_name() -> None:
    job_id = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    job = SimpleNamespace(
        id=job_id,
        name="SECRET INTERNAL NAME",
        service_type="Exterior painting",
        city="Decatur",
        published_at=datetime(2026, 8, 23, 15, 0, tzinfo=UTC),
    )
    package = SimpleNamespace(project_description="Two-story colonial, full body and trim.")
    assets = [
        SimpleNamespace(
            destination_type="conversion_site",
            title="Exterior painting in Decatur",
            body="Two-story colonial, full body and trim…",
        )
    ]
    item = serialize_demo_list_item(
        job,
        package,
        assets,
        primary_image_url="https://cdn.test/after.jpg",
        has_before=True,
        has_after=True,
    )
    dumped = item.model_dump(by_alias=True)
    assert "SECRET INTERNAL NAME" not in str(dumped)
    assert "name" not in dumped
    assert dumped["slug"] == "exterior-painting-in-decatur-a1b2"
    assert dumped["publicTitle"] == "Exterior painting in Decatur"
    assert dumped["serviceType"] == "Exterior painting"
    assert dumped["city"] == "Decatur"
    assert dumped["hasBefore"] is True
    assert dumped["hasAfter"] is True


def test_eligible_statuses_match_spec() -> None:
    assert ELIGIBLE_PUBLIC_STATUSES == {
        "ready_for_approval",
        "publishing",
        "published",
        "publish_issue",
    }


def _register(client: TestClient, email: str = "alex@example.com") -> dict:
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Alex Rivera", "email": email, "companyName": "Rivera Painting"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_ineligible_jobs_omitted_and_eligible_listed(client: TestClient, monkeypatch) -> None:
    import asyncio
    from datetime import UTC, datetime

    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.main import app
    from app.models.content import ContentPackage, GeneratedAsset
    from app.models.job import Job
    from app.models.media import MediaAsset

    _register(client)

    factory = app.state.test_session_factory

    async def insert_jobs() -> None:
        async with factory() as db:
            db: AsyncSession
            from app.models.company import Contractor

            contractor = (
                await db.execute(select(Contractor).where(Contractor.email == "alex@example.com"))
            ).scalar_one()
            draft = Job(
                company_id=contractor.company_id,
                created_by_contractor_id=contractor.id,
                name="HIDDEN DRAFT",
                service_type="Interior painting",
                city="Atlanta",
                public_status="active",
            )
            eligible = Job(
                company_id=contractor.company_id,
                created_by_contractor_id=contractor.id,
                name="HIDDEN ELIGIBLE",
                service_type="Exterior painting",
                city="Decatur",
                public_status="ready_for_approval",
                published_at=datetime.now(UTC),
            )
            db.add_all([draft, eligible])
            await db.flush()
            pkg = ContentPackage(
                company_id=contractor.company_id,
                job_id=eligible.id,
                version=1,
                status="ready_for_approval",
                project_description="Two-story colonial, full body and trim.",
            )
            db.add(pkg)
            await db.flush()
            after = MediaAsset(
                company_id=contractor.company_id,
                job_id=eligible.id,
                uploaded_by_contractor_id=contractor.id,
                kind="photo",
                photo_category="after",
                original_object_key="jobs/after.jpg",
                mime_type="image/jpeg",
                upload_status="complete",
            )
            before = MediaAsset(
                company_id=contractor.company_id,
                job_id=eligible.id,
                uploaded_by_contractor_id=contractor.id,
                kind="photo",
                photo_category="before",
                original_object_key="jobs/before.jpg",
                mime_type="image/jpeg",
                upload_status="complete",
            )
            db.add_all([before, after])
            await db.flush()
            pkg.featured_before_media_id = before.id
            pkg.featured_after_media_id = after.id
            for dest, title, body in (
                ("facebook", "FB title", "FB body"),
                ("instagram", "IG title", "IG body"),
                ("google_business", "GBP title", "GBP body"),
                ("conversion_site", "Exterior painting in Decatur", "Public write-up."),
            ):
                db.add(
                    GeneratedAsset(
                        company_id=contractor.company_id,
                        package_id=pkg.id,
                        destination_type=dest,
                        title=title,
                        body=body,
                        status="ready",
                    )
                )
            await db.flush()
            await db.commit()

    asyncio.run(insert_jobs())

    def fake_presign(self, key: str, *, expires_in: int | None = None) -> str:
        return f"https://cdn.test/{key}"

    monkeypatch.setattr(
        "app.integrations.storage.s3.ObjectStorage.presign_get", fake_presign
    )

    listed = client.get(
        "/api/v1/public/demo/projects",
        params={"email": "alex@example.com"},
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert len(items) == 1
    assert items[0]["city"] == "Decatur"
    assert "HIDDEN" not in str(items[0])
    assert items[0]["primaryImageUrl"] == "https://cdn.test/jobs/after.jpg"
    slug = items[0]["slug"]

    detail = client.get(
        f"/api/v1/public/demo/projects/{slug}",
        params={"email": "alex@example.com"},
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert "HIDDEN" not in str(body)
    dests = {p["destination"] for p in body["socialPosts"]}
    assert dests == {"facebook", "instagram", "google_business"}
    assert any(m["stageLabel"] == "before" for m in body["media"])
    assert any(m["stageLabel"] == "after" for m in body["media"])

    missing = client.get(
        "/api/v1/public/demo/projects/no-such-job-ffff",
        params={"email": "alex@example.com"},
    )
    assert missing.status_code == 404

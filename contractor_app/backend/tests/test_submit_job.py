"""POST /jobs/{id}/submit — the Finish Job button."""

from __future__ import annotations

import asyncio
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from fastapi.testclient import TestClient

from app.models.enums import MediaKind, UploadStatus
from app.models.media import MediaAsset


def _token(url: str) -> str:
    return parse_qs(urlparse(url).query)["token"][0]


def _authed_client(client: TestClient) -> tuple[str, dict]:
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alex Rivera",
            "email": "alex@example.com",
            "password": "secret123",
            "companyName": "Rivera Painting",
        },
    )
    assert reg.status_code == 201, reg.text
    verify = client.post(
        "/api/v1/auth/verify-email",
        json={"token": _token(reg.json()["verificationUrl"])},
    )
    assert verify.status_code == 200, verify.text
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "alex@example.com", "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    body = login.json()
    return body["accessToken"], body


def _add_ready_media(
    client: TestClient,
    *,
    job_id: str,
    company_id: str,
    contractor_id: str,
) -> None:
    async def _insert() -> None:
        async with client.app.state.test_session_factory() as session:
            for cat in ("before", "after"):
                session.add(
                    MediaAsset(
                        company_id=UUID(company_id),
                        job_id=UUID(job_id),
                        uploaded_by_contractor_id=UUID(contractor_id),
                        kind=MediaKind.photo.value,
                        photo_category=cat,
                        original_object_key=f"test/{job_id}/{cat}.jpg",
                        mime_type="image/jpeg",
                        byte_size=1200,
                        upload_status=UploadStatus.complete.value,
                    )
                )
            session.add(
                MediaAsset(
                    company_id=UUID(company_id),
                    job_id=UUID(job_id),
                    uploaded_by_contractor_id=UUID(contractor_id),
                    kind=MediaKind.audio.value,
                    original_object_key=f"test/{job_id}/voice.webm",
                    mime_type="audio/webm",
                    byte_size=8000,
                    duration_ms=4000,
                    upload_status=UploadStatus.complete.value,
                    is_active_voice=True,
                )
            )
            await session.commit()

    asyncio.run(_insert())


def test_submit_job_returns_processing_when_celery_enqueue_works(
    client: TestClient, monkeypatch
) -> None:
    token, session = _authed_client(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "name": "Deck stain",
            "serviceType": "Decks",
            "city": "Decatur",
            "region": "GA",
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]
    _add_ready_media(
        client,
        job_id=job_id,
        company_id=session["company"]["id"],
        contractor_id=session["contractor"]["id"],
    )

    monkeypatch.setattr(
        "app.api.v1.jobs.process_job_submission.delay",
        lambda *args, **kwargs: None,
    )

    resp = client.post(
        f"/api/v1/jobs/{job_id}/submit",
        headers=headers,
        json={"idempotencyKey": "submit-test-key-0001"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["publicStatus"] == "processing"


def test_submit_job_falls_back_to_inline_pipeline_when_celery_is_down(
    client: TestClient, monkeypatch
) -> None:
    token, session = _authed_client(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "name": "Deck stain",
            "serviceType": "Decks",
            "city": "Decatur",
            "region": "GA",
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]
    _add_ready_media(
        client,
        job_id=job_id,
        company_id=session["company"]["id"],
        contractor_id=session["contractor"]["id"],
    )

    monkeypatch.setattr(
        "app.api.v1.jobs.process_job_submission.delay",
        lambda *args, **kwargs: (_ for _ in ()).throw(ConnectionError("broker down")),
    )

    resp = client.post(
        f"/api/v1/jobs/{job_id}/submit",
        headers=headers,
        json={"idempotencyKey": "submit-test-key-0002"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["publicStatus"] in {"processing", "ready_for_approval"}


def test_update_job_does_not_500_after_flush(client: TestClient) -> None:
    token, _session = _authed_client(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "name": "Deck stain",
            "serviceType": "Decks",
            "city": "Decatur",
            "region": "GA",
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]
    resp = client.patch(
        f"/api/v1/jobs/{job_id}",
        headers=headers,
        json={"name": "Deck stain v2"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "Deck stain v2"

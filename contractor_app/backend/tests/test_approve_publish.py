"""POST /jobs/{id}/approve-and-publish must leave publishing, not freeze there."""

from __future__ import annotations

import asyncio
import threading
from uuid import UUID

from fastapi.testclient import TestClient

from app.services.engine import apply_publish
from tests.test_submit_job import _add_ready_media, _authed_client


def _ready_job(client: TestClient) -> tuple[dict[str, str], str]:
    token, session = _authed_client(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "name": "Porch paint",
            "serviceType": "Painting",
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
    submitted = client.post(
        f"/api/v1/jobs/{job_id}/submit",
        headers=headers,
        json={"idempotencyKey": "submit-then-publish-0001"},
    )
    assert submitted.status_code == 200, submitted.text
    status = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert status.status_code == 200, status.text
    assert status.json()["publicStatus"] == "ready_for_approval"
    return headers, job_id


def test_approve_and_publish_completes_without_celery_in_fake_mode(
    client: TestClient,
) -> None:
    headers, job_id = _ready_job(client)

    resp = client.post(
        f"/api/v1/jobs/{job_id}/approve-and-publish",
        headers=headers,
        json={"idempotencyKey": "publish-test-key-0001"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["publicStatus"] in {"publishing", "published"}

    status = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert status.status_code == 200, status.text
    assert status.json()["publicStatus"] == "published"
    assert status.json()["internalStatus"] == "published"
    assert status.json()["publishedAt"]


def test_approve_and_publish_does_not_overwrite_worker_result(
    client: TestClient, monkeypatch
) -> None:
    """If the worker finishes before the HTTP session closes, stay published."""
    headers, job_id = _ready_job(client)

    def _run_worker(job_id_s: str, package_id_s: str, key: str) -> None:
        async def _do() -> None:
            async with client.app.state.test_session_factory() as session:
                await apply_publish(session, UUID(job_id_s), UUID(package_id_s), key)
                await session.commit()

        def _in_thread() -> None:
            asyncio.run(_do())

        thread = threading.Thread(target=_in_thread)
        thread.start()
        thread.join()

    monkeypatch.setattr(
        "app.api.v1.packages.get_settings",
        lambda: type("S", (), {"provider_mode": "live"})(),
    )
    monkeypatch.setattr(
        "app.api.v1.packages.process_approve_and_publish.delay",
        _run_worker,
    )

    resp = client.post(
        f"/api/v1/jobs/{job_id}/approve-and-publish",
        headers=headers,
        json={"idempotencyKey": "publish-test-key-0002"},
    )
    assert resp.status_code == 200, resp.text

    status = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert status.status_code == 200, status.text
    assert status.json()["publicStatus"] == "published"
    assert status.json()["publishedAt"]


def test_approve_and_publish_resumes_a_stuck_publishing_job(
    client: TestClient, monkeypatch
) -> None:
    headers, job_id = _ready_job(client)

    monkeypatch.setattr(
        "app.api.v1.packages.get_settings",
        lambda: type("S", (), {"provider_mode": "live"})(),
    )
    monkeypatch.setattr(
        "app.api.v1.packages.process_approve_and_publish.delay",
        lambda *args, **kwargs: None,
    )

    stuck = client.post(
        f"/api/v1/jobs/{job_id}/approve-and-publish",
        headers=headers,
        json={"idempotencyKey": "publish-stuck-0001"},
    )
    assert stuck.status_code == 200, stuck.text
    assert stuck.json()["publicStatus"] == "publishing"

    monkeypatch.setattr(
        "app.api.v1.packages.get_settings",
        lambda: type("S", (), {"provider_mode": "fake"})(),
    )

    resumed = client.post(
        f"/api/v1/jobs/{job_id}/approve-and-publish",
        headers=headers,
        json={"idempotencyKey": "publish-resume-0001"},
    )
    assert resumed.status_code == 200, resumed.text

    status = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert status.status_code == 200, status.text
    assert status.json()["publicStatus"] == "published"

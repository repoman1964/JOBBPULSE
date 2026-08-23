"""Presigned URL shape for browser PUT/GET against R2."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from app.core.config import Settings
from app.integrations.storage.s3 import ObjectStorage


def _storage() -> ObjectStorage:
    return ObjectStorage(
        Settings(
            s3_endpoint_url="https://example.r2.cloudflarestorage.com",
            s3_public_endpoint_url="https://example.r2.cloudflarestorage.com",
            s3_access_key="AKIAEXAMPLE",
            s3_secret_key="secretsecretsecretsecret",
            s3_bucket="jobbpulse",
            s3_region="auto",
        )
    )


def test_presign_put_does_not_sign_checksum_headers() -> None:
    url, _expires = _storage().presign_put(
        "companies/c1/jobs/j1/photos/m1",
        content_type="image/jpeg",
    )
    signed = parse_qs(urlparse(url).query).get("X-Amz-SignedHeaders", [""])[0]
    headers = {h.strip() for h in signed.split(";") if h.strip()}
    assert "host" in headers
    assert "content-type" in headers
    assert not any("checksum" in h for h in headers)

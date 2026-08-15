"""S3-compatible object storage (MinIO in local dev)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
from botocore.client import Config

from app.core.config import Settings, get_settings


class ObjectStorage:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint_url,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        # Client for presigned URLs returned to the browser (public host)
        public_endpoint = (
            self.settings.s3_public_endpoint_url or self.settings.s3_endpoint_url
        )
        self._public_client = boto3.client(
            "s3",
            endpoint_url=public_endpoint,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = self.settings.s3_bucket

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket)
        except Exception:
            self._client.create_bucket(Bucket=self.bucket)

    def presign_put(
        self,
        key: str,
        *,
        content_type: str,
        expires_in: int | None = None,
    ) -> tuple[str, datetime]:
        ttl = expires_in or self.settings.upload_url_ttl_seconds
        url = self._public_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=ttl,
        )
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
        return url, expires_at

    def presign_get(self, key: str, *, expires_in: int | None = None) -> str:
        ttl = expires_in or self.settings.download_url_ttl_seconds
        return self._public_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=ttl,
        )

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def head_object(self, key: str) -> dict[str, Any] | None:
        try:
            return self._client.head_object(Bucket=self.bucket, Key=key)
        except Exception:
            return None

    def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

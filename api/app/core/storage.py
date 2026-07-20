"""S3-compatible object storage (MinIO locally, R2/S3 in production)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

import boto3
from botocore.client import BaseClient, Config
from botocore.exceptions import ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heif",
}


@lru_cache
def get_s3_client() -> BaseClient:
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint or None,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def ensure_bucket() -> None:
    """Create the app bucket if missing (dev / MinIO)."""
    settings = get_settings()
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        try:
            client.create_bucket(Bucket=settings.s3_bucket)
            logger.info("Created S3 bucket %s", settings.s3_bucket)
        except ClientError as exc:
            logger.warning("Could not create bucket %s: %s", settings.s3_bucket, exc)


def build_storage_key(
    company_id: str,
    job_id: str,
    media_id: str,
    mime_type: str,
    original_filename: Optional[str] = None,
) -> str:
    ext = MIME_TO_EXT.get(mime_type.lower())
    if not ext and original_filename and "." in original_filename:
        ext = original_filename.rsplit(".", 1)[-1].lower()[:10]
    if not ext:
        ext = "bin"
    return f"companies/{company_id}/jobs/{job_id}/media/{media_id}.{ext}"


def presign_put_url(storage_key: str, mime_type: str, expires_in: int = 3600) -> str:
    settings = get_settings()
    client = get_s3_client()
    return client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket,
            "Key": storage_key,
            "ContentType": mime_type,
        },
        ExpiresIn=expires_in,
    )


def presign_get_url(storage_key: str, expires_in: int = 3600) -> str:
    settings = get_settings()
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": storage_key},
        ExpiresIn=expires_in,
    )


def object_exists(storage_key: str) -> bool:
    settings = get_settings()
    client = get_s3_client()
    try:
        client.head_object(Bucket=settings.s3_bucket, Key=storage_key)
        return True
    except ClientError:
        return False


def put_bytes(storage_key: str, body: bytes, mime_type: str) -> None:
    settings = get_settings()
    client = get_s3_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=storage_key,
        Body=body,
        ContentType=mime_type,
    )


def delete_object(storage_key: str) -> None:
    settings = get_settings()
    client = get_s3_client()
    try:
        client.delete_object(Bucket=settings.s3_bucket, Key=storage_key)
    except ClientError as exc:
        logger.warning("Failed to delete %s: %s", storage_key, exc)


def public_or_signed_url(storage_key: str, *, signed: bool = True) -> str:
    """
    Return a delivery URL for an object.

    Private job media should use signed=True (default). Public directory
    assets may pass signed=False when the key lives under a public prefix.
    """
    settings = get_settings()
    if not signed and settings.s3_public_base_url:
        base = settings.s3_public_base_url.rstrip("/")
        return f"{base}/{storage_key}"
    return rewrite_presigned_for_browser(presign_get_url(storage_key))


def is_allowed_image_mime(mime_type: str) -> bool:
    return mime_type.lower() in ALLOWED_IMAGE_MIME_TYPES


def rewrite_presigned_for_browser(url: str) -> str:
    """
    Ensure presigned URLs use the host-visible S3 endpoint from settings.
    (No-op when endpoint already matches.)
    """
    settings = get_settings()
    if not settings.s3_endpoint:
        return url
    target = urlparse(settings.s3_endpoint)
    parsed = urlparse(url)
    if not target.scheme or not target.netloc:
        return url
    return parsed._replace(scheme=target.scheme, netloc=target.netloc).geturl()

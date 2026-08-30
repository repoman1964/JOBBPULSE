"""Slug helpers for company public identifiers."""

import re
import unicodedata
import uuid
from uuid import UUID


def slugify(value: str, *, max_length: int = 180) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if not value:
        value = "item"
    return value[:max_length].strip("-") or "item"


def public_project_slug(public_title: str, job_id: UUID) -> str:
    return f"{slugify(public_title, max_length=60)}-{job_id.hex[:4]}"


def unique_company_slug(name: str) -> str:
    base = slugify(name)[:180]
    suffix = uuid.uuid4().hex[:6]
    return f"{base}-{suffix}"

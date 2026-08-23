"""URL-safe kebab-case slugs."""

from __future__ import annotations

import re
import unicodedata
from uuid import UUID


def slugify(value: str, *, max_length: int = 80) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    kebab = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if not kebab:
        kebab = "item"
    return kebab[:max_length].strip("-") or "item"


def public_project_slug(public_title: str, job_id: UUID) -> str:
    return f"{slugify(public_title, max_length=60)}-{job_id.hex[:4]}"

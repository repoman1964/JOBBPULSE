"""Slug helpers for company public identifiers."""

import re
import uuid


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "company"


def unique_company_slug(name: str) -> str:
    base = slugify(name)[:180]
    suffix = uuid.uuid4().hex[:6]
    return f"{base}-{suffix}"

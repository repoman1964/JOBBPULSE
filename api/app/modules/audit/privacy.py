"""Scrub secrets and private fields from audit payloads."""

from __future__ import annotations

from typing import Any, Optional

# Keys that must never land in audit JSON (case-insensitive match on leaf keys)
_SECRET_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "credentials",
        "credentials_encrypted",
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "secret",
        "authorization",
        "storage_key",
        "jwt",
        "stripe_webhook_secret",
        "app_secret_key",
        "s3_secret_key",
        "publishing_api_key",
    }
)

_PRIVATE_FIELD_KEYS = frozenset(
    {
        "title",  # private job title
        "job_title",
        "customer_name_private",
        "notes",
    }
)


def scrub_value(value: Any, *, private_title: Optional[str] = None) -> Any:
    """Recursively scrub a JSON-serializable structure for audit storage."""
    if value is None:
        return None
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            key_l = str(k).lower()
            if key_l in _SECRET_KEYS or any(s in key_l for s in ("password", "credential", "secret", "token")):
                out[k] = "[REDACTED]"
                continue
            if key_l in _PRIVATE_FIELD_KEYS:
                out[k] = "[PRIVATE]"
                continue
            out[k] = scrub_value(v, private_title=private_title)
        return out
    if isinstance(value, list):
        return [scrub_value(v, private_title=private_title) for v in value]
    if isinstance(value, str):
        if private_title and private_title.strip() and private_title in value:
            return value.replace(private_title, "[PRIVATE_TITLE]")
        return value
    if isinstance(value, (int, float, bool)):
        return value
    # UUID, datetime, enums → string
    return str(value)


def scrub_payload(
    payload: Optional[dict[str, Any]],
    *,
    private_title: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    if payload is None:
        return None
    scrubbed = scrub_value(payload, private_title=private_title)
    return scrubbed if isinstance(scrubbed, dict) else {"value": scrubbed}

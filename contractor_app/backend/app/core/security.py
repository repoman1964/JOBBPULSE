"""JWT access tokens, password hashing, and refresh token helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from base64 import b64decode, b64encode
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from app.core.config import Settings

_PBKDF2_ITERATIONS = 210_000


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return (
        f"pbkdf2_sha256${_PBKDF2_ITERATIONS}$"
        f"{b64encode(salt).decode()}${b64encode(digest).decode()}"
    )


def verify_password(password: str, stored: str | None) -> bool:
    if not stored or stored.count("$") != 3:
        return False
    algo, iter_s, salt_b64, hash_b64 = stored.split("$", 3)
    if algo != "pbkdf2_sha256":
        return False
    try:
        iterations = int(iter_s)
        salt = b64decode(salt_b64)
        expected = b64decode(hash_b64)
    except (ValueError, TypeError):
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected)


def hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def generate_otp(length: int = 6) -> str:
    # Cryptographically secure digits
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def create_access_token(
    *,
    settings: Settings,
    contractor_id: UUID,
    company_id: UUID,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(contractor_id),
        "company_id": str(company_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.access_token_ttl_minutes)).timestamp()
        ),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "sub", "type"]},
    )

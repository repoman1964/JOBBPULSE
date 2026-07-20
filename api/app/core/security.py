"""Password hashing and JWT helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _encode(payload: dict[str, Any], expires_delta: timedelta) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + expires_delta
    data["iat"] = datetime.now(timezone.utc)
    return jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: UUID, company_id: Optional[UUID] = None) -> str:
    payload: dict[str, Any] = {"sub": str(user_id), "type": "access"}
    if company_id:
        payload["company_id"] = str(company_id)
    return _encode(payload, timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(user_id: UUID) -> str:
    return _encode(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def safe_decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return decode_token(token)
    except JWTError:
        return None

"""Standard API envelope helpers."""

from typing import Any


def success(data: Any = None, meta: dict | None = None) -> dict:
    return {"data": data, "meta": meta or {}, "error": None}


def failure(code: str, message: str, details: dict | None = None, meta: dict | None = None) -> dict:
    return {
        "data": None,
        "meta": meta or {},
        "error": {"code": code, "message": message, "details": details or {}},
    }

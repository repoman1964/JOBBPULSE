"""Consistent API error envelope."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        field_errors: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field_errors = field_errors
        super().__init__(message)


def error_body(
    code: str,
    message: str,
    field_errors: dict[str, str] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"code": code, "message": message}
    if field_errors:
        body["fieldErrors"] = field_errors
    return body


def _mark_rollback(request: Request) -> None:
    request.state.db_rollback = True


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    _mark_rollback(request)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, exc.field_errors),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    _mark_rollback(request)
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    message = detail if isinstance(detail, str) else "Request failed"
    code = "http_error"
    if exc.status_code == 401:
        code = "unauthorized"
    elif exc.status_code == 403:
        code = "forbidden"
    elif exc.status_code == 404:
        code = "not_found"
    elif exc.status_code == 409:
        code = "conflict"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, message),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    _mark_rollback(request)
    field_errors: dict[str, str] = {}
    for err in exc.errors():
        loc = err.get("loc") or ()
        # skip "body" prefix
        parts = [str(p) for p in loc if p not in {"body", "query", "path"}]
        key = ".".join(parts) if parts else "request"
        field_errors[key] = err.get("msg", "Invalid value")
    return JSONResponse(
        status_code=422,
        content=error_body(
            "validation_error",
            "Please check the highlighted fields and try again.",
            field_errors,
        ),
    )

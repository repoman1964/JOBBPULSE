"""HTTP middleware: request IDs and structured access logging.

Uses pure ASGI middleware (not BaseHTTPMiddleware) to avoid known
deadlocks with httpx AsyncClient / streaming responses.
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("jobpulse.request")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware:
    """Generate or propagate X-Request-ID; attach to scope state and response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope.get("headers") or []
        }
        request_id = (headers.get("x-request-id") or "").strip() or str(uuid.uuid4())

        # Starlette Request.state wraps scope["state"] when it is a dict
        state = scope.setdefault("state", {})
        if isinstance(state, dict):
            state["request_id"] = request_id
        else:
            setattr(state, "request_id", request_id)

        started = time.perf_counter()
        path = scope.get("path", "")
        method = scope.get("method", "")
        status_code_holder = {"code": 500}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_code_holder["code"] = int(message.get("status", 500))
                raw_headers = list(message.get("headers") or [])
                raw_headers.append(
                    (b"x-request-id", request_id.encode("latin-1"))
                )
                message = {**message, "headers": raw_headers}
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "request_failed method=%s path=%s request_id=%s duration_ms=%.1f",
                method,
                path,
                request_id,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - started) * 1000
        if path not in {"/health", "/health/live", "/health/ready"}:
            logger.info(
                "request method=%s path=%s status=%s request_id=%s duration_ms=%.1f",
                method,
                path,
                status_code_holder["code"],
                request_id,
                duration_ms,
            )


def get_request_id(request: Request | None) -> str | None:
    if request is None:
        return None
    return getattr(request.state, "request_id", None)

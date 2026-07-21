"""
JobPulse API — FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.middleware import RequestIdMiddleware, get_request_id
from app.core.responses import failure, success
from app.db.session import engine
from app.modules.admin.api import router as admin_router
from app.modules.ai_generation.api import router as generation_router
from app.modules.audit.api import router as audit_router
from app.modules.auth.api import router as auth_router
from app.modules.billing.api import router as billing_router
from app.modules.companies.api import router as company_router
from app.modules.content.api import router as content_router
from app.modules.directory.api import router as directory_router
from app.modules.directory.public_api import router as public_directory_router
from app.modules.jobs.api import router as jobs_router
from app.modules.notifications.api import router as notifications_router
from app.modules.publishing.api import router as publishing_router

settings = get_settings()
logger = logging.getLogger("jobpulse")


def _configure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO if settings.app_env != "development" else logging.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )


def _init_sentry() -> None:
    dsn = (settings.sentry_dsn or "").strip()
    if not dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=settings.app_env,
            release=f"jobpulse-api@{settings.app_version}",
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
            traces_sample_rate=0.1 if settings.app_env != "development" else 0.0,
        )
        logger.info("sentry_initialized")
    except ImportError:
        logger.warning("SENTRY_DSN set but sentry-sdk is not installed; skipping")
    except Exception:  # noqa: BLE001
        logger.exception("sentry_init_failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    _init_sentry()
    try:
        from app.core.storage import ensure_bucket

        ensure_bucket()
    except Exception:  # noqa: BLE001 — storage may be down during boot
        pass
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for JobPulse — job-to-marketing for visual home-service contractors.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(company_router, prefix=settings.api_v1_prefix)
app.include_router(jobs_router, prefix=settings.api_v1_prefix)
app.include_router(generation_router, prefix=settings.api_v1_prefix)
app.include_router(content_router, prefix=settings.api_v1_prefix)
app.include_router(directory_router, prefix=settings.api_v1_prefix)
app.include_router(public_directory_router, prefix=settings.api_v1_prefix)
app.include_router(publishing_router, prefix=settings.api_v1_prefix)
app.include_router(audit_router, prefix=settings.api_v1_prefix)
app.include_router(notifications_router, prefix=settings.api_v1_prefix)
app.include_router(billing_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)


def _meta_with_request_id(request: Request, meta: dict | None = None) -> dict:
    out = dict(meta or {})
    rid = get_request_id(request)
    if rid:
        out["request_id"] = rid
    return out


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.warning(
        "app_error code=%s status=%s request_id=%s message=%s",
        exc.code,
        exc.status_code,
        get_request_id(request),
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=failure(exc.code, exc.message, exc.details, meta=_meta_with_request_id(request)),
    )


def _json_safe_validation_errors(errors: list) -> list:
    """Pydantic may put Exception objects in error ctx; make them JSON-safe."""
    safe: list = []
    for err in errors:
        item = dict(err)
        ctx = item.get("ctx")
        if isinstance(ctx, dict):
            item["ctx"] = {
                k: (str(v) if isinstance(v, BaseException) else v) for k, v in ctx.items()
            }
        safe.append(item)
    return safe


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=failure(
            "VALIDATION_ERROR",
            "Request validation failed.",
            {"errors": _json_safe_validation_errors(exc.errors())},
            meta=_meta_with_request_id(request),
        ),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_error request_id=%s path=%s",
        get_request_id(request),
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content=failure(
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
            meta=_meta_with_request_id(request),
        ),
    )


@app.get("/")
async def root(request: Request):
    return success(
        {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "api": settings.api_v1_prefix,
        },
        meta=_meta_with_request_id(request),
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/live")
async def health_live():
    return {"status": "live"}


@app.get("/health/ready")
async def health_ready():
    checks: dict = {"database": "ok", "redis": "skipped", "s3": "skipped"}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 — readiness should not raise
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "error", "detail": str(exc), "checks": checks},
        )

    # Soft dependency checks — do not fail readiness solely on redis/s3 for pilot
    try:
        import redis.asyncio as redis_async

        client = redis_async.from_url(settings.redis_url, socket_connect_timeout=0.5)
        try:
            await client.ping()
            checks["redis"] = "ok"
        finally:
            await client.aclose()
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc}"

    try:
        from app.core.storage import ensure_bucket

        ensure_bucket()
        checks["s3"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["s3"] = f"error: {exc}"

    return {"status": "ready", "database": "ok", "checks": checks}


@app.get(f"{settings.api_v1_prefix}/status")
async def api_status(request: Request):
    return success(
        {
            "env": settings.app_env,
            "version": settings.app_version,
            "ai_provider": settings.ai_provider,
            "publishing_provider": settings.publishing_provider,
            "transcription_provider": settings.transcription_provider,
            "billing_enforce": settings.billing_enforce,
            "sentry_enabled": bool((settings.sentry_dsn or "").strip()),
        },
        meta=_meta_with_request_id(request),
    )

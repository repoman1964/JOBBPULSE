"""
JobPulse API — FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.responses import failure, success
from app.db.session import engine
from app.modules.ai_generation.api import router as generation_router
from app.modules.auth.api import router as auth_router
from app.modules.companies.api import router as company_router
from app.modules.jobs.api import router as jobs_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(company_router, prefix=settings.api_v1_prefix)
app.include_router(jobs_router, prefix=settings.api_v1_prefix)
app.include_router(generation_router, prefix=settings.api_v1_prefix)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=failure(exc.code, exc.message, exc.details),
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
async def validation_error_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=failure(
            "VALIDATION_ERROR",
            "Request validation failed.",
            {"errors": _json_safe_validation_errors(exc.errors())},
        ),
    )


@app.get("/")
async def root():
    return success(
        {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "api": settings.api_v1_prefix,
        }
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/live")
async def health_live():
    return {"status": "live"}


@app.get("/health/ready")
async def health_ready():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception as exc:  # noqa: BLE001 — readiness should not raise
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "error", "detail": str(exc)},
        )


@app.get(f"{settings.api_v1_prefix}/status")
async def api_status():
    return success(
        {
            "env": settings.app_env,
            "ai_provider": settings.ai_provider,
            "publishing_provider": settings.publishing_provider,
            "transcription_provider": settings.transcription_provider,
        }
    )

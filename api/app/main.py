"""
JobPulse API — FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.responses import success

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup hooks (DB warm-up, storage checks) land here in later phases.
    yield


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
    # Phase 1+: check DB / Redis connectivity.
    return {"status": "ready"}


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

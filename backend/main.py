"""
JobPulse — FastAPI application entry point.
Backend for the JobPulse mobile app.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from db.database import init_db
from services.storage import init_storage
from routers import jobs, content


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and storage on startup."""
    await init_db()
    await init_storage()
    print("✓ Database initialized")
    print("✓ Storage directories ready")
    yield
    print("→ Shutting down JobPulse API")


app = FastAPI(
    title="JobPulse API",
    description="Backend API for JobPulse — turn job-site photos and voice notes into social media content.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
# Allow the Nuxt dev server and Capacitor app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # Nuxt dev server
        "http://localhost:3001",       # Alternate port
        "capacitor://localhost",       # Capacitor Android
        "http://localhost",            # Capacitor iOS
        "*",                           # Dev: allow all (restrict in prod)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (serve uploaded photos) ──────────────────
upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# ── Routers ───────────────────────────────────────────────
app.include_router(jobs.router)
app.include_router(content.router)


@app.get("/")
async def root():
    return {
        "app": "JobPulse API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

"""
JobPulse — Job CRUD router.
Handles job creation with file uploads, listing, and retrieval.
"""

import uuid
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from db.database import get_db
from db.models import JobResponse, JobListItem, JobStats, PhotoResponse, ContentResponse
from services.storage import save_photo, save_audio

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=dict)
async def create_job(
    job_type: str = Form(...),
    title: Optional[str] = Form(None),
    customer_name: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    platforms: str = Form('["facebook","gbp","blog"]'),
    photos: list[UploadFile] = File(default=[]),
    audio: Optional[UploadFile] = File(None),
):
    """
    Create a new job with photos and optional voice note.
    Accepts multipart form data.
    """
    job_id = str(uuid.uuid4())
    db = await get_db()

    try:
        # Save photos
        saved_photos = []
        for i, photo in enumerate(photos):
            if photo.filename:
                result = await save_photo(photo, job_id)
                result["sort_order"] = i
                saved_photos.append(result)

        # Save audio
        audio_path = None
        if audio and audio.filename:
            audio_path = await save_audio(audio, job_id)

        # Insert job
        await db.execute(
            """INSERT INTO jobs 
               (id, job_type, title, customer_name, voice_audio_path,
                latitude, longitude, city, state, address, platforms, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job_id, job_type, title, customer_name, audio_path,
                latitude, longitude, city, state, address, platforms,
                "pending"
            ),
        )

        # Insert photos
        for photo in saved_photos:
            await db.execute(
                """INSERT INTO job_photos (id, job_id, file_path, original_name, sort_order)
                   VALUES (?, ?, ?, ?, ?)""",
                (photo["id"], job_id, photo["file_path"], photo["original_name"], photo["sort_order"]),
            )

        await db.commit()

        return {
            "id": job_id,
            "status": "pending",
            "photo_count": len(saved_photos),
            "has_audio": audio_path is not None,
            "message": "Job created successfully. Call /api/jobs/{id}/generate to process.",
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()


@router.get("", response_model=list[JobListItem])
async def list_jobs(limit: int = 50, offset: int = 0):
    """List all jobs with summary info, newest first."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT j.id, j.job_type, j.title, j.customer_name, j.status,
                      j.city, j.created_at, j.voice_audio_path,
                      (SELECT COUNT(*) FROM job_photos WHERE job_id = j.id) as photo_count
               FROM jobs j
               ORDER BY j.created_at DESC
               LIMIT ? OFFSET ?""",
            (limit, offset),
        )
        rows = await cursor.fetchall()

        return [
            JobListItem(
                id=row["id"],
                job_type=row["job_type"],
                title=row["title"],
                customer_name=row["customer_name"],
                status=row["status"],
                photo_count=row["photo_count"],
                has_voice=row["voice_audio_path"] is not None,
                city=row["city"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
    finally:
        await db.close()


@router.get("/stats", response_model=JobStats)
async def get_stats():
    """Get dashboard statistics."""
    db = await get_db()
    try:
        # Total jobs
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM jobs")
        total = (await cursor.fetchone())["cnt"]

        # Jobs this month
        cursor = await db.execute(
            """SELECT COUNT(*) as cnt FROM jobs 
               WHERE created_at >= date('now', 'start of month')"""
        )
        this_month = (await cursor.fetchone())["cnt"]

        # Published
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM jobs WHERE status = 'published'"
        )
        published = (await cursor.fetchone())["cnt"]

        return JobStats(
            total_jobs=total,
            jobs_this_month=this_month,
            published_count=published,
            total_impressions=0,  # v2: integrate analytics
        )
    finally:
        await db.close()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get full job details including photos and generated content."""
    db = await get_db()
    try:
        # Get job
        cursor = await db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job = await cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get photos
        cursor = await db.execute(
            "SELECT * FROM job_photos WHERE job_id = ? ORDER BY sort_order",
            (job_id,),
        )
        photos = await cursor.fetchall()

        # Get content
        cursor = await db.execute(
            "SELECT * FROM generated_content WHERE job_id = ? ORDER BY created_at",
            (job_id,),
        )
        content = await cursor.fetchall()

        return JobResponse(
            id=job["id"],
            job_type=job["job_type"],
            title=job["title"],
            customer_name=job["customer_name"],
            voice_transcript=job["voice_transcript"],
            latitude=job["latitude"],
            longitude=job["longitude"],
            city=job["city"],
            state=job["state"],
            address=job["address"],
            platforms=job["platforms"],
            status=job["status"],
            created_at=job["created_at"],
            photos=[
                PhotoResponse(
                    id=p["id"],
                    file_path=p["file_path"],
                    original_name=p["original_name"],
                    sort_order=p["sort_order"],
                )
                for p in photos
            ],
            content=[
                ContentResponse(
                    id=c["id"],
                    platform=c["platform"],
                    title=c["title"],
                    body=c["body"],
                    hashtags=c["hashtags"],
                    published=bool(c["published"]),
                    published_at=c["published_at"],
                    created_at=c["created_at"],
                )
                for c in content
            ],
        )
    finally:
        await db.close()

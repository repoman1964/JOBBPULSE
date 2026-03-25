"""
JobPulse — Content generation and publishing router.
Handles the Whisper → GPT pipeline and third-party publishing.
"""

import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException

from db.database import get_db
from db.models import ContentResponse, ContentEdit, GenerateRequest, PublishRequest
from services.speech_to_text import transcribe_audio
from services.content_generator import generate_content
from services.posting import publish_content

router = APIRouter(prefix="/api/jobs", tags=["content"])


@router.post("/{job_id}/generate", response_model=dict)
async def generate_job_content(job_id: str, request: GenerateRequest | None = None):
    """
    Run the full content generation pipeline:
    1. Transcribe voice note (Whisper)
    2. Generate platform-specific posts (GPT-4)
    3. Store generated content in database

    This maps to the Processing screen's 4-step pipeline.
    """
    db = await get_db()
    try:
        # Get the job
        cursor = await db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job = await cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Update status to processing
        await db.execute(
            "UPDATE jobs SET status = 'processing', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), job_id),
        )
        await db.commit()

        # ── Step 1: Transcribe voice note ───────────────────
        transcript = job["voice_transcript"]  # May already exist
        if not transcript and job["voice_audio_path"]:
            transcript = await transcribe_audio(job["voice_audio_path"])
            await db.execute(
                "UPDATE jobs SET voice_transcript = ? WHERE id = ?",
                (transcript, job_id),
            )
            await db.commit()

        if not transcript:
            # No audio and no transcript — use job metadata as input
            transcript = f"{job['job_type']} job completed"
            if job["title"]:
                transcript = f"{job['title']} - {transcript}"

        # ── Step 2: Build location string ───────────────────
        location_parts = []
        if job["address"]:
            location_parts.append(job["address"])
        if job["city"]:
            location_parts.append(job["city"])
        if job["state"]:
            location_parts.append(job["state"])
        location = ", ".join(location_parts) if location_parts else "Location not specified"

        # ── Step 3: Get photo count ─────────────────────────
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM job_photos WHERE job_id = ?", (job_id,)
        )
        photo_count = (await cursor.fetchone())["cnt"]

        # ── Step 4: Generate content via GPT ────────────────
        platforms = json.loads(job["platforms"])
        tone = request.tone if request else None
        custom_instructions = request.custom_instructions if request else None

        generated = await generate_content(
            job_type=job["job_type"],
            transcript=transcript,
            location=location,
            platforms=platforms,
            title=job["title"],
            customer_name=job["customer_name"],
            photo_count=photo_count,
            tone=tone,
            custom_instructions=custom_instructions,
        )

        # ── Step 5: Delete old content and store new ────────
        await db.execute(
            "DELETE FROM generated_content WHERE job_id = ?", (job_id,)
        )

        content_items = []
        for platform in platforms:
            if platform in generated:
                item = generated[platform]
                content_id = str(uuid.uuid4())
                await db.execute(
                    """INSERT INTO generated_content 
                       (id, job_id, platform, title, body, hashtags)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        content_id, job_id, platform,
                        item.get("title"),
                        item.get("body", ""),
                        item.get("hashtags"),
                    ),
                )
                content_items.append({
                    "id": content_id,
                    "platform": platform,
                    "title": item.get("title"),
                    "body": item.get("body", ""),
                    "hashtags": item.get("hashtags"),
                })

        # Update job status
        await db.execute(
            "UPDATE jobs SET status = 'draft', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), job_id),
        )
        await db.commit()

        return {
            "job_id": job_id,
            "status": "draft",
            "transcript": transcript,
            "content": content_items,
            "message": "Content generated successfully.",
        }

    except HTTPException:
        raise
    except Exception as e:
        # Revert status on failure
        await db.execute(
            "UPDATE jobs SET status = 'failed', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), job_id),
        )
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()


@router.put("/{job_id}/content/{content_id}", response_model=dict)
async def edit_content(job_id: str, content_id: str, edit: ContentEdit):
    """Edit generated content before publishing (maps to Edit button)."""
    db = await get_db()
    try:
        # Verify content exists and belongs to job
        cursor = await db.execute(
            "SELECT * FROM generated_content WHERE id = ? AND job_id = ?",
            (content_id, job_id),
        )
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Content not found")

        updates = []
        values = []
        if edit.title is not None:
            updates.append("title = ?")
            values.append(edit.title)
        if edit.body is not None:
            updates.append("body = ?")
            values.append(edit.body)
        if edit.hashtags is not None:
            updates.append("hashtags = ?")
            values.append(edit.hashtags)

        if updates:
            values.append(content_id)
            await db.execute(
                f"UPDATE generated_content SET {', '.join(updates)} WHERE id = ?",
                values,
            )
            await db.commit()

        return {"message": "Content updated successfully."}
    finally:
        await db.close()


@router.post("/{job_id}/publish", response_model=dict)
async def publish_job_content(job_id: str, request: PublishRequest | None = None):
    """
    Publish generated content to platforms via third-party API.
    Maps to the Publish / Publish All buttons.
    """
    db = await get_db()
    try:
        # Get job
        cursor = await db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job = await cursor.fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get content to publish
        if request and request.platforms:
            placeholders = ",".join("?" * len(request.platforms))
            cursor = await db.execute(
                f"""SELECT * FROM generated_content 
                    WHERE job_id = ? AND platform IN ({placeholders}) AND published = 0""",
                [job_id] + request.platforms,
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM generated_content WHERE job_id = ? AND published = 0",
                (job_id,),
            )
        content_rows = await cursor.fetchall()

        if not content_rows:
            raise HTTPException(status_code=400, detail="No unpublished content found")

        # Get photo paths
        cursor = await db.execute(
            "SELECT file_path FROM job_photos WHERE job_id = ? ORDER BY sort_order",
            (job_id,),
        )
        photo_rows = await cursor.fetchall()
        photo_paths = [r["file_path"] for r in photo_rows]

        # Build location dict
        location = None
        if job["latitude"] and job["longitude"]:
            location = {
                "lat": job["latitude"],
                "lng": job["longitude"],
                "address": job["address"],
                "city": job["city"],
                "state": job["state"],
            }

        # Publish each content item
        results = []
        now = datetime.utcnow().isoformat()
        for content in content_rows:
            result = await publish_content(
                platform=content["platform"],
                title=content["title"],
                body=content["body"],
                hashtags=content["hashtags"],
                photo_paths=photo_paths,
                location=location,
            )
            results.append(result)

            # Mark as published if successful
            if result.get("success"):
                await db.execute(
                    """UPDATE generated_content 
                       SET published = 1, published_at = ?, publish_response = ?
                       WHERE id = ?""",
                    (now, json.dumps(result.get("response", {})), content["id"]),
                )

        # Update job status if all published
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM generated_content WHERE job_id = ? AND published = 0",
            (job_id,),
        )
        unpublished = (await cursor.fetchone())["cnt"]
        if unpublished == 0:
            await db.execute(
                "UPDATE jobs SET status = 'published', updated_at = ? WHERE id = ?",
                (now, job_id),
            )

        await db.commit()

        return {
            "job_id": job_id,
            "results": results,
            "all_published": unpublished == 0,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()

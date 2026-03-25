"""
JobPulse — File storage service.
Handles saving uploaded photos and audio files to disk.
"""

import os
import uuid
import aiofiles
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


async def init_storage():
    """Create upload directories if they don't exist."""
    for subdir in ["photos", "audio"]:
        path = os.path.join(UPLOAD_DIR, subdir)
        os.makedirs(path, exist_ok=True)


async def save_photo(file: UploadFile, job_id: str) -> dict:
    """
    Save an uploaded photo to disk.
    Returns dict with file_path and original_name.
    """
    ext = os.path.splitext(file.filename or "photo.jpg")[1] or ".jpg"
    photo_id = str(uuid.uuid4())
    filename = f"{job_id}_{photo_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, "photos", filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {
        "id": photo_id,
        "file_path": file_path,
        "original_name": file.filename,
    }


async def save_audio(file: UploadFile, job_id: str) -> str:
    """
    Save an uploaded audio file to disk.
    Returns the file path.
    """
    ext = os.path.splitext(file.filename or "voice.webm")[1] or ".webm"
    filename = f"{job_id}_voice{ext}"
    file_path = os.path.join(UPLOAD_DIR, "audio", filename)

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    return file_path


def get_photo_url(file_path: str, base_url: str = "") -> str:
    """Convert a file path to a servable URL."""
    return f"{base_url}/uploads/{os.path.relpath(file_path, UPLOAD_DIR)}"

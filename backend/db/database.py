"""
JobPulse — SQLite database setup and schema initialization.
Uses aiosqlite for async operations.
"""

import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "./jobpulse.db")


async def get_db() -> aiosqlite.Connection:
    """Get an async database connection."""
    db = await aiosqlite.connect(DATABASE_URL)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                title TEXT,
                customer_name TEXT,
                voice_audio_path TEXT,
                voice_transcript TEXT,
                latitude REAL,
                longitude REAL,
                city TEXT,
                state TEXT,
                address TEXT,
                platforms TEXT DEFAULT '["facebook","gbp","blog"]',
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS job_photos (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                file_path TEXT NOT NULL,
                original_name TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS generated_content (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                platform TEXT NOT NULL,
                title TEXT,
                body TEXT NOT NULL,
                hashtags TEXT,
                published INTEGER DEFAULT 0,
                published_at DATETIME,
                publish_response TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_job_photos_job_id ON job_photos(job_id);
            CREATE INDEX IF NOT EXISTS idx_generated_content_job_id ON generated_content(job_id);
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
            CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
        """)
        await db.commit()
    finally:
        await db.close()

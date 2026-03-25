
"""
JobPulse — Third-party posting API client.
Sends generated content to an external service for publishing
to Facebook, Google Business Profile, and blog platforms.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

POSTING_API_URL = os.getenv("POSTING_API_URL", "")
POSTING_API_KEY = os.getenv("POSTING_API_KEY", "")


async def publish_content(
    platform: str,
    title: str | None,
    body: str,
    hashtags: str | None,
    photo_paths: list[str],
    location: dict | None = None,
) -> dict:
    """
    Publish content to a platform via the third-party posting API.

    Args:
        platform: 'facebook', 'gbp', or 'blog'
        title: Post title (used for blog and GBP)
        body: Post body text
        hashtags: Hashtag string
        photo_paths: List of local photo file paths to upload
        location: Dict with lat, lng, address, city, state

    Returns:
        API response dict with publish status and any metadata.
    """
    if not POSTING_API_URL:
        return {
            "success": False,
            "error": "Posting API URL not configured. Set POSTING_API_URL in .env",
            "platform": platform,
        }

    headers = {
        "Authorization": f"Bearer {POSTING_API_KEY}",
        "Accept": "application/json",
    }

    # Build the payload
    payload = {
        "platform": platform,
        "title": title,
        "body": body,
        "hashtags": hashtags,
    }

    if location:
        payload["location"] = location

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # If we have photos, send as multipart
            if photo_paths:
                files = []
                for i, path in enumerate(photo_paths):
                    if os.path.exists(path):
                        files.append(
                            ("photos", (os.path.basename(path), open(path, "rb")))
                        )

                response = await client.post(
                    f"{POSTING_API_URL}/publish",
                    headers=headers,
                    data=payload,
                    files=files,
                )

                # Close file handles
                for _, (_, fh) in files:
                    fh.close()
            else:
                response = await client.post(
                    f"{POSTING_API_URL}/publish",
                    headers=headers,
                    json=payload,
                )

            response.raise_for_status()

            return {
                "success": True,
                "platform": platform,
                "response": response.json(),
            }

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "platform": platform,
                "error": f"API returned {e.response.status_code}: {e.response.text}",
            }
        except Exception as e:
            return {
                "success": False,
                "platform": platform,
                "error": str(e),
            }

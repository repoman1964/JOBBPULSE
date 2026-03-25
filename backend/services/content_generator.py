"""
JobPulse — LLM content generation service using OpenAI GPT.
Generates platform-specific social media posts from job data.
"""

import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _build_system_prompt() -> str:
    return """You are a social media content writer for service contractors 
(HVAC, plumbing, electrical, roofing, landscaping, etc.).

You create engaging, professional posts that showcase completed work and 
attract new customers. You write in a confident, friendly tone that reflects 
the expertise of a skilled tradesperson.

Always include the location when provided. Never fabricate details — only 
use information given to you. If the contractor's description is brief, 
expand it naturally but stay truthful to what was described."""


def _build_user_prompt(
    job_type: str,
    transcript: str,
    location: str,
    title: str | None = None,
    customer_name: str | None = None,
    photo_count: int = 0,
) -> str:
    parts = [
        f"Job type: {job_type}",
        f"Contractor's voice note transcript: \"{transcript}\"",
        f"Location: {location}",
    ]
    if title:
        parts.append(f"Job title: {title}")
    if customer_name:
        parts.append(f"Customer: {customer_name}")
    if photo_count > 0:
        parts.append(f"Number of photos taken: {photo_count}")

    return "\n".join(parts)


async def generate_content(
    job_type: str,
    transcript: str,
    location: str,
    platforms: list[str],
    title: str | None = None,
    customer_name: str | None = None,
    photo_count: int = 0,
    tone: str | None = None,
    custom_instructions: str | None = None,
) -> dict:
    """
    Generate social media posts for the specified platforms.

    Returns dict keyed by platform with title, body, and hashtags.
    """
    user_prompt = _build_user_prompt(
        job_type=job_type,
        transcript=transcript,
        location=location,
        title=title,
        customer_name=customer_name,
        photo_count=photo_count,
    )

    platform_specs = []
    for p in platforms:
        if p == "facebook":
            platform_specs.append(
                "FACEBOOK POST: Casual and engaging. 2-3 paragraphs max. "
                "Include relevant emojis. End with a call to action. "
                "Add 3-5 relevant hashtags at the bottom."
            )
        elif p == "gbp":
            platform_specs.append(
                "GOOGLE BUSINESS PROFILE POST: Concise and professional. "
                "1-2 short paragraphs. Focus on the service and location. "
                "End with 'Request a quote today' or similar CTA. No hashtags."
            )
        elif p == "blog":
            platform_specs.append(
                "BLOG POST: SEO-friendly with a compelling title. "
                "3-4 paragraphs explaining what was done and why it matters. "
                "Use the job location in the title for local SEO. "
                "Professional but approachable tone. Include 3-5 hashtags."
            )

    generation_prompt = f"""{user_prompt}

Generate content for the following platforms:

{chr(10).join(platform_specs)}

{f"Tone: {tone}" if tone else ""}
{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Respond ONLY with valid JSON in this exact format:
{{
    "facebook": {{"title": null, "body": "...", "hashtags": "#tag1 #tag2"}},
    "gbp": {{"title": "Update: ...", "body": "...", "hashtags": null}},
    "blog": {{"title": "...", "body": "...", "hashtags": "#tag1 #tag2"}}
}}

Only include the platforms requested: {json.dumps(platforms)}"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": generation_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        content_text = response.choices[0].message.content
        return json.loads(content_text)

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse GPT response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Content generation failed: {str(e)}")

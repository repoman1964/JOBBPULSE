"""
JobPulse — Speech-to-text service using OpenAI Whisper API.
Transcribes voice notes recorded in the field.
"""

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file using OpenAI Whisper.

    Args:
        audio_path: Path to the audio file (webm, mp3, wav, etc.)

    Returns:
        Transcribed text string.
    """
    try:
        with open(audio_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                response_format="text",
                prompt=(
                    "This is a voice note from a service contractor describing "
                    "work they completed on a job site. It may include technical "
                    "terms related to HVAC, plumbing, electrical, roofing, "
                    "landscaping, or general contracting."
                ),
            )
        return response.strip() if isinstance(response, str) else str(response).strip()
    except Exception as e:
        raise Exception(f"Whisper transcription failed: {str(e)}")

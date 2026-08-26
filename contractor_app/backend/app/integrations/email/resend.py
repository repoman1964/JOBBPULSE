"""Send transactional email through Resend."""

from __future__ import annotations

import logging

import httpx

from app.core.config import Settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


def _from_address(from_value: str) -> str:
    if "<" in from_value:
        return from_value
    return f"JobbPulse <{from_value}>"


async def send_verification_email(
    *,
    settings: Settings,
    to_email: str,
    verify_url: str,
) -> None:
    subject = "Confirm your JobbPulse account"
    text = (
        "Thanks for signing up for JobbPulse.\n\n"
        "Confirm this email to activate your account:\n"
        f"{verify_url}\n\n"
        "If you did not create this account, you can ignore this message."
    )
    html = (
        "<p>Thanks for signing up for JobbPulse.</p>"
        "<p><a href=\""
        f"{verify_url}"
        "\">Confirm your email</a> to activate your account.</p>"
        "<p>If you did not create this account, you can ignore this message.</p>"
    )

    if not settings.resend_api_key:
        if settings.is_production:
            raise AppError(
                "email_not_configured",
                "Email delivery is not configured.",
                status_code=503,
            )
        logger.info("Verification email (dev, no Resend key) to=%s url=%s", to_email, verify_url)
        return

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                RESEND_URL,
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": _from_address(settings.auth_from_email),
                    "to": [to_email],
                    "subject": subject,
                    "text": text,
                    "html": html,
                },
            )
    except httpx.HTTPError as exc:
        logger.exception("Resend request failed")
        raise AppError(
            "email_send_failed",
            "We could not send the confirmation email. Try again in a moment.",
            status_code=503,
        ) from exc

    if response.is_success:
        return

    logger.error("Resend send failed status=%s body=%s", response.status_code, response.text)
    raise AppError(
        "email_send_failed",
        "We could not send the confirmation email. Try again in a moment.",
        status_code=503,
    )

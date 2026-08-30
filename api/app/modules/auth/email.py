"""Send transactional email through Resend."""

from __future__ import annotations

import logging

import httpx

from app.core.config import Settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


def _from_address(from_value: str) -> str:
    if "<" in from_value:
        return from_value
    return f"JobbPulse <{from_value}>"


async def _deliver_email(
    *,
    settings: Settings,
    to_email: str,
    subject: str,
    text: str,
    html: str,
    log_label: str,
    failure_message: str,
    debug_url: str | None = None,
) -> None:
    api_key = (settings.resend_api_key or "").strip()
    from_addr = _from_address(settings.email_from)
    local_from = "localhost" in from_addr.lower() or "noreply@localhost" in from_addr.lower()
    if not api_key or local_from:
        reason = "no RESEND_API_KEY" if not api_key else "localhost EMAIL_FROM"
        if settings.is_production:
            logger.error("Email delivery is not configured (%s); cannot send %s email", reason, log_label)
            raise AppError(
                "EMAIL_NOT_CONFIGURED",
                "Email delivery is not configured.",
                status_code=503,
            )
        logger.info(
            "%s email (dev, skipped live send: %s) to=%s url=%s",
            log_label,
            reason,
            to_email,
            debug_url or "",
        )
        return

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                RESEND_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": from_addr,
                    "to": [to_email],
                    "subject": subject,
                    "text": text,
                    "html": html,
                },
            )
    except httpx.HTTPError as exc:
        logger.exception("Resend request failed")
        raise AppError("EMAIL_SEND_FAILED", failure_message, status_code=503) from exc

    if response.is_success:
        resend_id = None
        try:
            payload = response.json()
            if isinstance(payload, dict):
                resend_id = payload.get("id")
        except Exception:
            pass
        logger.info(
            "%s email sent to=%s from=%s resend_id=%s",
            log_label,
            to_email,
            from_addr,
            resend_id,
        )
        return

    logger.error(
        "Resend send failed status=%s from=%s to=%s body=%s",
        response.status_code,
        from_addr,
        to_email,
        response.text,
    )
    lowered = response.text.lower()
    if "own email address" in lowered or "verify a domain" in lowered:
        logger.error(
            "Resend rejected AUTH_FROM_EMAIL/EMAIL_FROM=%s. "
            "Use an address on the verified jobbpulse.com domain.",
            from_addr,
        )
    raise AppError("EMAIL_SEND_FAILED", failure_message, status_code=503)


async def send_verification_email(*, settings: Settings, to_email: str, verify_url: str) -> None:
    await _deliver_email(
        settings=settings,
        to_email=to_email,
        subject="Confirm your JobbPulse account",
        text=(
            "Thanks for signing up for JobbPulse.\n\n"
            "Confirm this email to activate your account:\n"
            f"{verify_url}\n\n"
            "If you did not create this account, you can ignore this message."
        ),
        html=(
            "<p>Thanks for signing up for JobbPulse.</p>"
            f'<p><a href="{verify_url}">Confirm your email</a> to activate your account.</p>'
            "<p>If you did not create this account, you can ignore this message.</p>"
        ),
        log_label="Verification",
        failure_message="We could not send the confirmation email. Try again in a moment.",
        debug_url=verify_url,
    )


async def send_password_reset_email(*, settings: Settings, to_email: str, reset_url: str) -> None:
    await _deliver_email(
        settings=settings,
        to_email=to_email,
        subject="Reset your JobbPulse password",
        text=(
            "We received a request to reset the password for this JobbPulse account.\n\n"
            "Choose a new password:\n"
            f"{reset_url}\n\n"
            "This link expires in one hour. If you did not ask to reset your password, "
            "you can ignore this message."
        ),
        html=(
            "<p>We received a request to reset the password for this JobbPulse account.</p>"
            f'<p><a href="{reset_url}">Choose a new password</a>.</p>'
            "<p>This link expires in one hour. If you did not ask to reset your password, "
            "you can ignore this message.</p>"
        ),
        log_label="Password reset",
        failure_message="We could not send the reset email. Try again in a moment.",
        debug_url=reset_url,
    )

"""Authentication: signup, email verify, password login, legacy OTP."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import AppSettings, CurrentAuth, DbSession
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    generate_otp,
    generate_refresh_token,
    hash_otp,
    hash_token,
    verify_password,
)
from app.models.auth import AuthChallenge, AuthIdentity, RefreshToken
from app.models.company import Contractor
from app.models.enums import ContractorStatus
from app.schemas.common import (
    ChallengeOut,
    RegisterOut,
    SessionOut,
    VerifyEmailOut,
)
from app.schemas.requests import (
    ChallengeRequest,
    LoginRequest,
    RegisterRequest,
    ResendVerificationRequest,
    VerifyChallengeRequest,
    VerifyEmailRequest,
)
from app.services.auth_email import activate_email, send_signup_verification
from app.services.auth_register import register_owner
from app.services.mappers import company_to_out, contractor_to_out

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[\d\s().-]{7,}$")


def _classify_identifier(identifier: str) -> str:
    value = identifier.strip()
    if EMAIL_RE.match(value):
        return "email"
    if PHONE_RE.match(value):
        return "phone"
    raise AppError(
        "invalid_identifier",
        "Enter a valid email or phone number.",
        status_code=422,
        field_errors={"identifier": "Enter a valid email or phone number."},
    )


def _normalize(identifier: str, kind: str) -> str:
    value = identifier.strip()
    if kind == "email":
        return value.lower()
    return re.sub(r"[^\d+]", "", value)


def _set_refresh_cookie(response: Response, raw_token: str, settings) -> None:
    max_age = settings.refresh_token_ttl_days * 24 * 3600
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=raw_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        max_age=max_age,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response, settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path="/api/v1/auth",
        domain=settings.cookie_domain,
    )


def _sign_in_redirect(settings, *, verified: bool) -> RedirectResponse:
    query = urlencode({"verified": "1" if verified else "0"})
    url = f"{settings.frontend_base_url.rstrip('/')}/sign-in?{query}"
    return RedirectResponse(url=url, status_code=302)


async def _issue_session(
    *,
    response: Response,
    db: DbSession,
    settings,
    contractor: Contractor,
    provider: str,
    provider_subject: str,
) -> SessionOut:
    now = datetime.now(UTC)
    result = await db.execute(
        select(AuthIdentity).where(
            AuthIdentity.provider == provider,
            AuthIdentity.provider_subject == provider_subject,
        )
    )
    identity = result.scalar_one_or_none()
    if identity is None:
        db.add(
            AuthIdentity(
                contractor_id=contractor.id,
                provider=provider,
                provider_subject=provider_subject,
                last_authenticated_at=now,
            )
        )
    else:
        identity.last_authenticated_at = now

    raw_refresh = generate_refresh_token()
    db.add(
        RefreshToken(
            contractor_id=contractor.id,
            token_hash=hash_token(raw_refresh),
            expires_at=now + timedelta(days=settings.refresh_token_ttl_days),
        )
    )
    await db.flush()

    access = create_access_token(
        settings=settings,
        contractor_id=contractor.id,
        company_id=contractor.company_id,
    )
    _set_refresh_cookie(response, raw_refresh, settings)
    return SessionOut(
        accessToken=access,
        contractor=contractor_to_out(contractor),
        company=company_to_out(contractor.company),
    )


@router.post("/register", response_model=RegisterOut, status_code=201)
async def register_account(
    body: RegisterRequest,
    db: DbSession,
    settings: AppSettings,
) -> RegisterOut:
    _company, contractor = await register_owner(
        db,
        name=body.name,
        email=str(body.email),
        company_name=body.company_name,
        password=body.password,
        phone=(body.phone or "").strip(),
    )
    verify_url = await send_signup_verification(
        db, contractor=contractor, settings=settings
    )
    return RegisterOut(
        email=contractor.email,
        companyId=contractor.company_id,
        contractorId=contractor.id,
        verificationUrl=(
            verify_url if settings.return_verification_url_to_client else None
        ),
    )


@router.post("/verify-email", response_model=VerifyEmailOut)
async def verify_email_post(body: VerifyEmailRequest, db: DbSession) -> VerifyEmailOut:
    contractor = await activate_email(db, body.token)
    return VerifyEmailOut(email=contractor.email, verified=True)


@router.get("/verify-email")
async def verify_email_get(
    db: DbSession,
    settings: AppSettings,
    token: str = Query(min_length=8, max_length=255),
) -> RedirectResponse:
    try:
        await activate_email(db, token)
    except AppError:
        return _sign_in_redirect(settings, verified=False)
    return _sign_in_redirect(settings, verified=True)


@router.post("/resend-verification", status_code=204)
async def resend_verification(
    body: ResendVerificationRequest,
    db: DbSession,
    settings: AppSettings,
) -> None:
    email = str(body.email).strip().lower()
    result = await db.execute(select(Contractor).where(Contractor.email == email))
    contractor = result.scalar_one_or_none()
    if contractor is None:
        return
    if contractor.email_verified_at is not None:
        return
    if contractor.status != ContractorStatus.pending.value:
        return
    await send_signup_verification(db, contractor=contractor, settings=settings)


@router.post("/login", response_model=SessionOut)
async def login(
    body: LoginRequest,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> SessionOut:
    email = str(body.email).strip().lower()
    result = await db.execute(
        select(Contractor)
        .where(Contractor.email == email)
        .options(selectinload(Contractor.company))
    )
    contractor = result.scalar_one_or_none()
    if contractor is None or not verify_password(body.password, contractor.password_hash):
        raise AppError(
            "invalid_credentials",
            "That email or password is not correct.",
            status_code=401,
        )
    if (
        contractor.email_verified_at is None
        or contractor.status == ContractorStatus.pending.value
    ):
        raise AppError(
            "email_not_verified",
            "Confirm your email before signing in. Check your inbox for the link.",
            status_code=403,
        )
    if contractor.status != ContractorStatus.active.value:
        raise AppError("unknown_user", "Account not found or inactive.", status_code=401)

    return await _issue_session(
        response=response,
        db=db,
        settings=settings,
        contractor=contractor,
        provider="email",
        provider_subject=email,
    )


@router.post("/challenge", response_model=ChallengeOut)
async def request_challenge(
    body: ChallengeRequest,
    db: DbSession,
    settings: AppSettings,
) -> ChallengeOut:
    kind = _classify_identifier(body.identifier)
    normalized = _normalize(body.identifier, kind)

    contractor: Contractor | None = None
    if kind == "email":
        result = await db.execute(
            select(Contractor).where(Contractor.email == normalized)
        )
        contractor = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(Contractor).where(Contractor.phone == normalized)
        )
        contractor = result.scalar_one_or_none()
        if contractor is None:
            # try loose match on digits
            result = await db.execute(select(Contractor))
            for c in result.scalars().all():
                if re.sub(r"[^\d+]", "", c.phone or "") == normalized:
                    contractor = c
                    break

    if settings.auth_dev_codes and not settings.is_production:
        code = settings.auth_fixed_dev_code
    else:
        code = generate_otp(6)

    challenge = AuthChallenge(
        identifier=normalized,
        identifier_type=kind,
        code_hash=hash_otp(code),
        expires_at=datetime.now(UTC)
        + timedelta(minutes=settings.auth_challenge_ttl_minutes),
        contractor_id=contractor.id if contractor else None,
    )
    db.add(challenge)
    await db.flush()

    logger.info(
        "auth_challenge created id=%s identifier=%s contractor=%s",
        challenge.id,
        normalized,
        contractor.id if contractor else None,
    )
    show_code = settings.return_otp_to_client
    if show_code:
        logger.warning("OTP shown in API response for %s (no email sent)", normalized)

    return ChallengeOut(
        challengeId=challenge.id,
        devCode=code if show_code else None,
    )


@router.post("/verify", response_model=SessionOut)
async def verify_challenge(
    body: VerifyChallengeRequest,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> SessionOut:
    result = await db.execute(
        select(AuthChallenge).where(AuthChallenge.id == body.challenge_id)
    )
    challenge = result.scalar_one_or_none()
    if challenge is None:
        raise AppError("invalid_challenge", "That code is no longer valid.", status_code=400)

    now = datetime.now(UTC)

    def _aware(dt: datetime) -> datetime:
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)

    if challenge.consumed_at is not None:
        raise AppError("challenge_used", "That code was already used.", status_code=400)
    if _aware(challenge.expires_at) < now:
        raise AppError(
            "challenge_expired",
            "That code expired. Request a new one.",
            status_code=400,
        )
    if challenge.attempt_count >= challenge.max_attempts:
        raise AppError(
            "too_many_attempts",
            "Too many attempts. Request a new code.",
            status_code=429,
        )

    challenge.attempt_count += 1
    if hash_otp(body.code.strip()) != challenge.code_hash:
        await db.flush()
        raise AppError("invalid_code", "That code does not match. Try again.", status_code=400)

    challenge.consumed_at = now

    if challenge.contractor_id is None:
        raise AppError(
            "unknown_user",
            "No account found for that email or phone. Ask your admin to invite you.",
            status_code=404,
        )

    result = await db.execute(
        select(Contractor)
        .where(Contractor.id == challenge.contractor_id)
        .options(selectinload(Contractor.company))
    )
    contractor = result.scalar_one_or_none()
    if contractor is None or contractor.status != "active":
        raise AppError("unknown_user", "Account not found or inactive.", status_code=404)

    return await _issue_session(
        response=response,
        db=db,
        settings=settings,
        contractor=contractor,
        provider=challenge.identifier_type,
        provider_subject=challenge.identifier,
    )


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> None:
    _clear_refresh_cookie(response, settings)


@router.post("/refresh", response_model=SessionOut)
async def refresh_session(
    response: Response,
    db: DbSession,
    settings: AppSettings,
    # Cookie read via Request would be cleaner; accept optional body later
) -> SessionOut:
    # Implemented via cookie in main path — use FastAPI Request
    raise AppError(
        "not_implemented_via_body",
        "Use cookie-based refresh from the HTTP client.",
        status_code=501,
    )


@router.get("/me", response_model=SessionOut)
async def me(auth: CurrentAuth, settings: AppSettings) -> SessionOut:
    # Re-issue short-lived access so frontend can treat getSession as session check
    access = create_access_token(
        settings=settings,
        contractor_id=auth.contractor_id,
        company_id=auth.company_id,
    )
    return SessionOut(
        accessToken=access,
        contractor=contractor_to_out(auth.contractor),
        company=company_to_out(auth.company),
    )

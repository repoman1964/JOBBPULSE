"""Auth HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_auth_context, get_current_user, AuthContext
from app.core.exceptions import AppError
from app.core.responses import success
from app.db.models import User
from app.db.session import get_db
from app.modules.auth import service
from app.core.config import get_settings
from app.core.rate_limit import get_limiter
from app.modules.auth.email import send_password_reset_email, send_verification_email
from app.modules.auth.schemas import (
    CompanySummaryOut,
    ForgotPasswordRequest,
    LoginRequest,
    MeOut,
    MembershipOut,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenPairOut,
    UserOut,
    VerifyEmailRequest,
)
from app.modules.phone.serialize import session_out

router = APIRouter(prefix="/auth", tags=["auth"])


def _membership_out(membership) -> MembershipOut | None:
    if membership is None:
        return None
    return MembershipOut(
        id=membership.id,
        company_id=membership.company_id,
        role=membership.role.value,
        status=membership.status.value,
    )


def _company_out(company) -> CompanySummaryOut | None:
    if company is None:
        return None
    return CompanySummaryOut.model_validate(company)


def _token_response(user: User, company, membership) -> dict:
    access, refresh = service.issue_tokens(user, company)
    if company is None:
        return success(
            TokenPairOut(
                access_token=access,
                refresh_token=refresh,
                user=UserOut.model_validate(user),
                company=None,
                membership=None,
            ).model_dump(mode="json")
        )
    payload = session_out(
        access_token=access,
        refresh_token=refresh,
        user=user,
        company=company,
        membership=membership,
    )
    payload["permissions"] = service.permissions_for_role(
        membership.role if membership else None
    )
    return success(payload)


def _check_auth_rate(request: Request, name: str) -> None:
    settings = get_settings()
    ip = request.client.host if request.client else "unknown"
    limiter = get_limiter(name, settings.auth_challenge_rate_per_minute)
    if not limiter.allow(ip):
        raise AppError(
            "RATE_LIMITED",
            "Too many requests. Try again in a minute.",
            status_code=429,
        )


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user, company, _membership = await service.register_user(db, body)
    verify_url = service.verification_url_for(user)
    settings = get_settings()
    await send_verification_email(
        settings=settings, to_email=user.email, verify_url=verify_url
    )
    data = {
        "email": user.email,
        "companyId": str(company.id),
        "contractorId": str(user.id),
        "company_id": str(company.id),
        "user_id": str(user.id),
    }
    if settings.return_verification_url_to_client:
        data["verificationUrl"] = verify_url
    return success(data)


@router.post("/verify-email")
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    user = await service.verify_email_token(db, body.token)
    return success({"email": user.email, "verified": True})


@router.post("/resend-verification")
async def resend_verification(
    body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
):
    user = await service.resend_verification(db, str(body.email))
    settings = get_settings()
    data: dict = {}
    if user is not None:
        verify_url = service.verification_url_for(user)
        await send_verification_email(
            settings=settings, to_email=user.email, verify_url=verify_url
        )
        if settings.return_verification_url_to_client:
            data["verificationUrl"] = verify_url
    return success(data or {"ok": True})


@router.get("/verify-email")
async def verify_email_get(
    db: AsyncSession = Depends(get_db),
    token: str = Query(min_length=8, max_length=2000),
):
    settings = get_settings()
    base = settings.frontend_url.rstrip("/")
    try:
        await service.verify_email_token(db, token)
    except AppError:
        return RedirectResponse(url=f"{base}/sign-in?verified=0", status_code=302)
    return RedirectResponse(url=f"{base}/sign-in?verified=1", status_code=302)


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _check_auth_rate(request, "forgot_password")
    settings = get_settings()
    user = await service.user_for_password_reset(db, str(body.email))
    reset_url = None
    if user is not None:
        reset_url = service.password_reset_url_for(user)
        await send_password_reset_email(
            settings=settings, to_email=user.email, reset_url=reset_url
        )
    return success(
        {
            "resetUrl": reset_url if settings.return_verification_url_to_client else None,
        }
    )


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    _check_auth_rate(request, "reset_password")
    user = await service.apply_password_reset(db, body.token, body.password)
    return success({"email": user.email, "reset": True})


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user, company, membership = await service.authenticate(db, body)
    return _token_response(user, company, membership)


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    user, company, membership = await service.refresh_tokens(db, body.refresh_token)
    return _token_response(user, company, membership)


@router.post("/logout")
async def logout():
    # Stateless JWT: client discards tokens. Hook for token denylist later.
    return success({"logged_out": True})


@router.get("/me")
async def me(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await service._primary_membership(db, user.id)
    company = membership.company if membership else None
    role = membership.role if membership else None
    access, _refresh = service.issue_tokens(user, company)
    if company is None:
        payload = MeOut(
            user=UserOut.model_validate(user),
            company=None,
            membership=None,
            permissions=service.permissions_for_role(role),
        )
        return success(payload.model_dump(mode="json"))
    data = session_out(
        access_token=access,
        user=user,
        company=company,
        membership=membership,
    )
    data["permissions"] = service.permissions_for_role(role)
    return success(data)


@router.get("/context")
async def auth_context(ctx: AuthContext = Depends(get_auth_context)):
    """Authenticated company context (requires active membership)."""
    return success(
        {
            "user": UserOut.model_validate(ctx.user).model_dump(mode="json"),
            "company": CompanySummaryOut.model_validate(ctx.company).model_dump(mode="json"),
            "membership": _membership_out(ctx.membership).model_dump(mode="json"),
            "permissions": service.permissions_for_role(ctx.role),
        }
    )

"""Auth HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_auth_context, get_current_user, AuthContext
from app.core.responses import success
from app.db.models import User
from app.db.session import get_db
from app.modules.auth import service
from app.core.config import get_settings
from app.modules.auth.schemas import (
    CompanySummaryOut,
    LoginRequest,
    MeOut,
    MembershipOut,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
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


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user, company, _membership = await service.register_user(db, body)
    verify_url = service.verification_url_for(user)
    settings = get_settings()
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
    if user is not None and settings.return_verification_url_to_client:
        data["verificationUrl"] = service.verification_url_for(user)
    return success(data or {"ok": True})


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

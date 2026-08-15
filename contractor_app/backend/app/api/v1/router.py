"""Aggregate API v1 routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, company, jobs, media, packages, social
from app.core.deps import AppSettings, CurrentAuth
from app.core.security import create_access_token
from app.schemas.common import SessionOut
from app.services.mappers import company_to_out, contractor_to_out

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(company.router)
api_router.include_router(jobs.router)
api_router.include_router(media.router)
api_router.include_router(packages.router)
api_router.include_router(social.router)


@api_router.get("/me", response_model=SessionOut, tags=["auth"])
async def get_me(auth: CurrentAuth, settings: AppSettings) -> SessionOut:
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

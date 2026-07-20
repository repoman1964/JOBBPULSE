"""Unauthenticated public directory API (§10.12)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success
from app.db.session import get_db
from app.modules.directory import service
from app.modules.directory.schemas import LeadCreate

router = APIRouter(prefix="/public", tags=["public-directory"])


@router.get("/contractors")
async def list_contractors(
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    trade: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items = await service.public_list_contractors(
        db, city=city, state=state, trade=trade, limit=limit, offset=offset
    )
    return success({"items": items, "limit": limit, "offset": offset})


@router.get("/contractors/{slug}")
async def get_contractor(slug: str, db: AsyncSession = Depends(get_db)):
    payload = await service.public_get_contractor(db, slug)
    return success(payload)


@router.get("/projects")
async def list_projects(
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    service_key: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items = await service.public_list_projects(
        db, city=city, state=state, service_key=service_key, limit=limit, offset=offset
    )
    return success({"items": items, "limit": limit, "offset": offset})


@router.get("/projects/{slug}")
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    payload = await service.public_get_project(db, slug)
    return success(payload)


@router.post("/leads")
async def create_lead(body: LeadCreate, db: AsyncSession = Depends(get_db)):
    payload = await service.create_lead_stub(
        db,
        contractor_slug=body.contractor_slug,
        name=body.name,
        email=body.email,
        phone=body.phone,
        message=body.message,
        project_slug=body.project_slug,
    )
    return success(payload)

"""Unauthenticated public directory / local portfolio API."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success
from app.db.session import get_db
from app.modules.directory import service
from app.modules.directory.schemas import LeadCreate

router = APIRouter(prefix="/public", tags=["public-directory"])


@router.get("/home")
async def home(db: AsyncSession = Depends(get_db)):
    payload = await service.public_home(db)
    return success(payload)


@router.get("/contractors")
async def list_contractors(
    q: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    trade: Optional[str] = Query(default=None),
    service_key: Optional[str] = Query(default=None),
    featured: Optional[bool] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items = await service.public_list_contractors(
        db,
        q=q,
        city=city,
        state=state,
        trade=trade,
        service_key=service_key,
        featured=featured,
        limit=limit,
        offset=offset,
    )
    return success({"items": items, "limit": limit, "offset": offset})


@router.get("/contractors/{slug}")
async def get_contractor(
    slug: str,
    project_limit: int = Query(default=50, ge=1, le=100),
    project_offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.public_get_contractor(
        db, slug, project_limit=project_limit, project_offset=project_offset
    )
    return success(payload)


@router.get("/projects")
async def list_projects(
    q: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    service_key: Optional[str] = Query(default=None),
    contractor_slug: Optional[str] = Query(default=None),
    featured: Optional[bool] = Query(default=None),
    has_before_after: Optional[bool] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items = await service.public_list_projects(
        db,
        q=q,
        city=city,
        state=state,
        service_key=service_key,
        contractor_slug=contractor_slug,
        featured=featured,
        has_before_after=has_before_after,
        limit=limit,
        offset=offset,
    )
    return success({"items": items, "limit": limit, "offset": offset})


@router.get("/projects/{slug}")
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    payload = await service.public_get_project(db, slug)
    return success(payload)


@router.get("/services")
async def list_services(db: AsyncSession = Depends(get_db)):
    items = await service.public_list_services(db)
    return success({"items": items})


@router.get("/services/{slug}")
async def get_service(slug: str, db: AsyncSession = Depends(get_db)):
    payload = await service.public_get_service(db, slug)
    return success(payload)


@router.get("/locations")
async def list_locations(db: AsyncSession = Depends(get_db)):
    items = await service.public_list_locations(db)
    return success({"items": items})


@router.get("/locations/{slug}")
async def get_location(slug: str, db: AsyncSession = Depends(get_db)):
    payload = await service.public_get_location(db, slug)
    return success(payload)


@router.get("/locations/{slug}/{service}")
async def get_location_service(
    slug: str, service: str, db: AsyncSession = Depends(get_db)
):
    payload = await service.public_get_location_service(db, slug, service)
    return success(payload)


@router.get("/search")
async def search(
    q: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    service_key: Optional[str] = Query(default=None),
    contractor_slug: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    payload = await service.public_search(
        db,
        q=q,
        city=city,
        state=state,
        service_key=service_key,
        contractor_slug=contractor_slug,
        limit=limit,
        offset=offset,
    )
    return success(payload)


@router.post("/leads")
async def create_lead(body: LeadCreate, db: AsyncSession = Depends(get_db)):
    payload = await service.create_lead(
        db,
        contractor_slug=body.contractor_slug,
        name=body.name,
        email=body.email,
        phone=body.phone,
        message=body.message,
        project_slug=body.project_slug,
        project_location=body.project_location,
        service_requested=body.service_requested,
        preferred_contact_method=body.preferred_contact_method,
        source_page_type=body.source_page_type,
        source_page_url=body.source_page_url,
    )
    return success(payload)

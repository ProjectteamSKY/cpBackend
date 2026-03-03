from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.size_domain import Size

from app.services.size_service import (
    create_size,
    get_all_sizes,
    get_size_by_id,
    update_size,
    delete_size,
    activate_size,
    deactivate_size,
    get_all_sizes_active
)

router = APIRouter()


@router.post("/create")
async def create_size_endpoint(
    name: str = Form(...),
    width: float = Form(...),
    height: float = Form(...),
    unit: str = Form("mm"),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session)
):

    size = Size(
        name=name,
        width=width,
        height=height,
        unit=unit,
        description=description
    )

    return await create_size(size, session)


@router.get("/list")
async def list_sizes(
    session: AsyncSession = Depends(get_session)
):

    return {
        "sizes": await get_all_sizes(session)
    }

@router.get("/list/active")
async def list_sizes(
    session: AsyncSession = Depends(get_session)
):

    return {
        "sizes": await get_all_sizes_active(session)
    }

@router.get("/{id}")
async def get_size_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await get_size_by_id(id, session)

    if not result:
        raise HTTPException(404, "Size not found")

    return result


@router.put("/{id}")
async def update_size_endpoint(
    id: str,
    name: str = Form(...),
    width: float = Form(...),
    height: float = Form(...),
    unit: str = Form(...),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session)
):

    result = await update_size(
        id,
        name,
        width,
        height,
        unit,
        description,
        session
    )

    if not result:
        raise HTTPException(404, "Size not found")

    return result


@router.delete("/{id}")
async def delete_size_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await delete_size(id, session)


@router.put("/{id}/activate")
async def activate_size_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await activate_size(id, session)

@router.put("/{id}/deactivate")
async def activate_size_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await deactivate_size(id, session)
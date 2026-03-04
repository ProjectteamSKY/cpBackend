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
):

    size = Size(
        name=name,
        width=width,
        height=height,
        unit=unit,
        description=description
    )

    return await create_size(size)


@router.get("/list")
async def list_sizes(
):

    return {
        "sizes": await get_all_sizes()
    }

@router.get("/list/active")
async def list_sizes(
):

    return {
        "sizes": await get_all_sizes_active()
    }

@router.get("/{id}")
async def get_size_endpoint(
    id: str,
):

    result = await get_size_by_id(id)

    if not result:
        raise HTTPException(404, "Size not found")

    return result



# UPDATE SIZE
@router.put("/{id}")
async def update_size_endpoint(
    id: str,
    name: str = Form(None),
    width: float = Form(None),
    height: float = Form(None),
    unit: str = Form(None),
    description: str = Form(None),
):

    # Build updates dict
    updates = {}
    if name is not None:
        updates["name"] = name
    if width is not None:
        updates["width"] = width
    if height is not None:
        updates["height"] = height
    if unit is not None:
        updates["unit"] = unit
    if description is not None:
        updates["description"] = description

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await update_size(id, updates)

    if not result:
        raise HTTPException(status_code=404, detail="Size not found")

    return result


@router.delete("/{id}")
async def delete_size_endpoint(
    id: str,
):

    return await delete_size(id)


@router.put("/{id}/activate")
async def activate_size_endpoint(
    id: str,
):

    return await activate_size(id)

@router.put("/{id}/deactivate")
async def activate_size_endpoint(
    id: str,
):

    return await deactivate_size(id)
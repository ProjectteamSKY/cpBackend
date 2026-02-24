from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.domain.subcategory_domain import Subcategory

from app.services.subcategory_service import (
    create_subcategory,
    get_all_subcategories,
    get_subcategory_by_id,
    get_subcategories_by_category,
    update_subcategory,
    delete_subcategory,
    activate_subcategory,
    deactivate_subcategory
)


router = APIRouter()


# CREATE
@router.post("/create")
async def create_subcategory_endpoint(
    category_id: str = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    is_active: bool = Form(True),
    session: AsyncSession = Depends(get_session)
):

    subcategory = Subcategory(
        category_id=category_id,
        name=name,
        description=description,
        is_active=is_active
    )

    return await create_subcategory(subcategory, session)


# LIST ALL
@router.get("/list")
async def list_subcategories(
    category_id: str = None,
    session: AsyncSession = Depends(get_session)
):

    if category_id:
        data = await get_subcategories_by_category(category_id, session)
    else:
        data = await get_all_subcategories(session)

    return {"subcategories": data}


# GET BY ID
@router.get("/{id}")
async def get_subcategory_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    data = await get_subcategory_by_id(id, session)

    if not data:
        raise HTTPException(404, "Subcategory not found")

    return data


# UPDATE
@router.put("/update/{id}")
async def update_subcategory_endpoint(
    id: str,
    name: str = Form(None),
    description: str = Form(None),
    is_active: bool = Form(None),
    session: AsyncSession = Depends(get_session)
):

    payload = {}

    if name is not None:
        payload["name"] = name

    if description is not None:
        payload["description"] = description

    if is_active is not None:
        payload["is_active"] = is_active

    if not payload:
        raise HTTPException(400, "No fields to update")

    result = await update_subcategory(id, payload, session)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return {
        "status": "success",
        "data": result
    }


# DELETE
@router.delete("/subcategory/{id}")
async def delete_subcategory_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await delete_subcategory(id, session)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return {
        "status": "success",
        "deleted_id": id
    }


# ACTIVATE
@router.put("/{id}/activate")
async def activate_subcategory_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await activate_subcategory(id, session)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return result


# DEACTIVATE
@router.put("/{id}/deactivate")
async def deactivate_subcategory_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await deactivate_subcategory(id, session)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return result
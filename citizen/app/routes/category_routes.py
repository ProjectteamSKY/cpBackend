from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

from app.domain.category_domain import Category

from app.services.category_service import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category,
    activate_category,
    deactivate_category
)

router = APIRouter()


# CREATE
@router.post("/category/create")
async def create_category_endpoint(
    name: str = Form(...),
    description: str = Form(None),
    is_active: bool = Form(True),
    session: AsyncSession = Depends(get_session)
):

    category = Category(
        name=name,
        description=description,
        is_active=is_active
    )

    return await create_category(category, session)


# LIST
@router.get("/categories/list")
async def list_categories(
    session: AsyncSession = Depends(get_session)
):

    categories = await get_all_categories(session)

    return {"categories": categories}


# GET BY ID
@router.get("/category/{id}")
async def get_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    category = await get_category_by_id(id, session)

    if not category:
        raise HTTPException(404, "Category not found")

    return category


# UPDATE
@router.put("/category/{id}")
async def update_category_endpoint(
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

    category = await update_category(
        id,
        payload,
        session
    )

    if not category:
        raise HTTPException(404, "Category not found")

    return {
        "status": "success",
        "data": category
    }


# DELETE
@router.delete("/category/{id}")
async def delete_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await delete_category(id, session)

    if not result:
        raise HTTPException(404, "Category not found")

    return {
        "status": "success",
        "deleted_id": id
    }


# ACTIVATE
@router.put("/category/{id}/activate")
async def activate_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await activate_category(id, session)

    if not result:
        raise HTTPException(404, "Category not found")

    return result


# DEACTIVATE
@router.put("/category/{id}/deactivate")
async def deactivate_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await deactivate_category(id, session)

    if not result:
        raise HTTPException(404, "Category not found")

    return result
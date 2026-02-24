from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel
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

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
# CREATE
@router.post("/create")
async def create_category_endpoint(
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_session)
):

    category = Category(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active
    )

    return await create_category(category, session)


# LIST
@router.get("/list")
async def list_categories(
    session: AsyncSession = Depends(get_session)
):

    categories = await get_all_categories(session)

    return {"categories": categories}


# GET BY ID
@router.get("/{id}")
async def get_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    category = await get_category_by_id(id, session)

    if not category:
        raise HTTPException(404, "Category not found")

    return category


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

# UPDATE
@router.put("/{id}")
async def update_category_endpoint(
    id: str,
    payload: CategoryUpdate,
    session: AsyncSession = Depends(get_session)
):
    # Pydantic v2 replacement for .dict()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    category = await update_category(
        id,
        update_data,
        session
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

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
@router.put("/{id}/activate")
async def activate_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await activate_category(id, session)

    if not result:
        raise HTTPException(404, "Category not found")

    return result


# DEACTIVATE
@router.put("/{id}/deactivate")
async def deactivate_category_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await deactivate_category(id, session)

    if not result:
        raise HTTPException(404, "Category not found")

    return result
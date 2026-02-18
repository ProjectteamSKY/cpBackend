# app/api/routes/category_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

from app.schemas.category_schema import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryResponseSchema
)

from app.services.category_service import (
    create_category_service,
    get_category_service,
    get_all_categories_service,
    update_category_service,
    delete_category_service
)

router = APIRouter()


@router.post("/", response_model=CategoryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_category_service(data, session)


@router.get("/", response_model=list[CategoryResponseSchema])
async def get_all_categories(session: AsyncSession = Depends(get_session)):
    return await get_all_categories_service(session)


@router.get("/{category_id}", response_model=CategoryResponseSchema)
async def get_category(category_id: str, session: AsyncSession = Depends(get_session)):
    category = await get_category_service(category_id, session)

    if not category:
        raise HTTPException(404, "Category not found")

    return category


@router.put("/{category_id}", response_model=CategoryResponseSchema)
async def update_category(category_id: str, data: CategoryUpdateSchema, session: AsyncSession = Depends(get_session)):
    updated = await update_category_service(category_id, data, session)

    if not updated:
        raise HTTPException(404, "Category not found")

    return updated


@router.delete("/{category_id}")
async def delete_category(category_id: str, session: AsyncSession = Depends(get_session)):
    success = await delete_category_service(category_id, session)

    if not success:
        raise HTTPException(404, "Category not found")

    return {"message": "Category deleted successfully"}

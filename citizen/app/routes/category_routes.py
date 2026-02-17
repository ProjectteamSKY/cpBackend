from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.category_schema import CategoryCreateSchema, CategoryResponseSchema
from app.services.category_service import create_category, get_category

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponseSchema)
async def create_category_route(data: CategoryCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_category(data, session)

@router.get("/{category_id}", response_model=CategoryResponseSchema)
async def get_category_route(category_id: str, session: AsyncSession = Depends(get_session)):
    category = await get_category(category_id, session)
    if not category:
        raise HTTPException(404, "Category not found")
    return category

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.subcategory_schema import SubCategoryCreateSchema, SubCategoryResponseSchema
from app.services.subcategory_service import create_subcategory, get_subcategory

router = APIRouter()

@router.post("/", response_model=SubCategoryResponseSchema)
async def create_subcategory_route(data: SubCategoryCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_subcategory(data, session)

@router.get("/{subcategory_id}", response_model=SubCategoryResponseSchema)
async def get_subcategory_route(subcategory_id: str, session: AsyncSession = Depends(get_session)):
    subcategory = await get_subcategory(subcategory_id, session)
    if not subcategory:
        raise HTTPException(404, "SubCategory not found")
    return subcategory

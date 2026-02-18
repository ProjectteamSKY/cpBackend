from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.subcategory_schema import (
    SubCategoryCreateSchema,
    SubCategoryResponseSchema,
    SubCategoryUpdateSchema
)
from app.services.subcategory_service import (
    create_subcategory,
    get_subcategory,
    get_subcategories,
    update_subcategory,
    delete_subcategory,
    get_all_subcategories,
    get_active_subcategories
)

router = APIRouter(prefix="/subcategories", tags=["SubCategories"])

# --- Specific routes first ---
# Get all subcategories (active + inactive)
@router.get("/all", response_model=list[SubCategoryResponseSchema])
async def get_all_subcategories_route(session: AsyncSession = Depends(get_session)):
    return await get_all_subcategories(session)

# Get only active subcategories
@router.get("/active", response_model=list[SubCategoryResponseSchema])
async def get_active_subcategories_route(session: AsyncSession = Depends(get_session)):
    return await get_active_subcategories(session)

# --- Catch-all routes after specific routes ---
# Create
@router.post("/", response_model=SubCategoryResponseSchema)
async def create_subcategory_route(data: SubCategoryCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_subcategory(data, session)

# Get single by ID
@router.get("/{subcategory_id}", response_model=SubCategoryResponseSchema)
async def get_subcategory_route(subcategory_id: str, session: AsyncSession = Depends(get_session)):
    subcategory = await get_subcategory(subcategory_id, session)
    if not subcategory:
        raise HTTPException(404, "SubCategory not found")
    return subcategory

# Get by category (optional query param)
@router.get("/", response_model=list[SubCategoryResponseSchema])
async def get_subcategories_route(category_id: str | None = None, session: AsyncSession = Depends(get_session)):
    return await get_subcategories(session, category_id)

# Update
@router.put("/{subcategory_id}", response_model=SubCategoryResponseSchema)
async def update_subcategory_route(subcategory_id: str, data: SubCategoryUpdateSchema, session: AsyncSession = Depends(get_session)):
    return await update_subcategory(subcategory_id, data.dict(exclude_unset=True), session)

# Soft delete
@router.delete("/{subcategory_id}")
async def delete_subcategory_route(subcategory_id: str, session: AsyncSession = Depends(get_session)):
    success = await delete_subcategory(subcategory_id, session)
    return {"detail": "SubCategory deleted successfully"}

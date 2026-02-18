from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.repository.subcategory_repository import (
    create_subcategory_repo,
    get_subcategory_by_id_repo,
    get_subcategories_repo,
    update_subcategory_repo,
    delete_subcategory_repo,
    get_all_subcategories_repo,
    get_active_subcategories_repo,
)
from app.domain.subcategory_domain import SubCategory
from app.db.models.product_models import Category as CategoryORM
from app.schemas.subcategory_schema import SubCategoryCreateSchema


# -------------------------------
# Helper: ensure category exists
# -------------------------------
async def ensure_category_exists(category_id: str, session: AsyncSession):
    result = await session.execute(select(CategoryORM).where(CategoryORM.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")


# -------------------------------
# Create SubCategory
# -------------------------------
async def create_subcategory(data: SubCategoryCreateSchema, session: AsyncSession) -> SubCategory:
    await ensure_category_exists(data.category_id, session)

    subcategory = SubCategory(
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        is_active=data.is_active if data.is_active is not None else True
    )
    return await create_subcategory_repo(subcategory, session)


# -------------------------------
# Get single SubCategory by ID
# -------------------------------
async def get_subcategory(subcategory_id: str, session: AsyncSession) -> SubCategory | None:
    subcategory = await get_subcategory_by_id_repo(subcategory_id, session)
    if not subcategory:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    return subcategory


# -------------------------------
# Get all SubCategories (optionally by category)
# -------------------------------
async def get_subcategories(session: AsyncSession, category_id: str | None = None) -> list[SubCategory]:
    if category_id:
        await ensure_category_exists(category_id, session)
    return await get_subcategories_repo(session, category_id)


# -------------------------------
# Update SubCategory
# -------------------------------
async def update_subcategory(subcategory_id: str, data: dict, session: AsyncSession) -> SubCategory:
    if "category_id" in data:
        await ensure_category_exists(data["category_id"], session)

    updated = await update_subcategory_repo(subcategory_id, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    return updated


# -------------------------------
# Soft Delete SubCategory
# -------------------------------
async def delete_subcategory(subcategory_id: str, session: AsyncSession) -> bool:
    success = await delete_subcategory_repo(subcategory_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    return success


# -------------------------------
# Get all SubCategories (active + inactive)
# -------------------------------
async def get_all_subcategories(session: AsyncSession) -> list[SubCategory]:
    return await get_all_subcategories_repo(session)


# -------------------------------
# Get only active SubCategories
# -------------------------------
async def get_active_subcategories(session: AsyncSession) -> list[SubCategory]:
    return await get_active_subcategories_repo(session)

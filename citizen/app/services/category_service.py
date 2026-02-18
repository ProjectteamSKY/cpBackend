# app/services/category_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.category_domain import Category
from app.repository.category_repository import (
    create_category_repo,
    get_category_by_id_repo,
    get_all_categories_repo,
    update_category_repo,
    delete_category_repo
)


async def create_category_service(data, session: AsyncSession):
    category = Category(
        name=data.name,
        description=data.description,
        is_active=data.is_active
    )
    return await create_category_repo(category, session)


async def get_category_service(category_id: str, session: AsyncSession):
    return await get_category_by_id_repo(category_id, session)


async def get_all_categories_service(session: AsyncSession):
    return await get_all_categories_repo(session)


async def update_category_service(category_id: str, data, session: AsyncSession):

    existing = await get_category_by_id_repo(category_id, session)

    if not existing:
        return None

    if data.name is not None:
        existing.name = data.name

    if data.description is not None:
        existing.description = data.description

    if data.is_active is not None:
        existing.is_active = data.is_active

    return await update_category_repo(existing, session)


async def delete_category_service(category_id: str, session: AsyncSession):
    return await delete_category_repo(category_id, session)

from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.category_domain import Category as CategoryDomain
from app.repository.category_repository import create_category_repo, get_category_by_id_repo

async def create_category(data, session: AsyncSession):
    category = CategoryDomain(name=data.name, description=data.description, is_active=data.is_active)
    return await create_category_repo(category, session)

async def get_category(category_id: str, session: AsyncSession):
    return await get_category_by_id_repo(category_id, session)

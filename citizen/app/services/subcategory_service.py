

from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.subcategory_repository import create_subcategory_repo, get_subcategory_by_id_repo
from app.domain.subcategory_domain import SubCategory as SubCategoryDomain

async def create_subcategory(data, session: AsyncSession):
    subcategory = SubCategoryDomain(name=data.name, description=data.description,
                                    category_id=data.category_id, is_active=data.is_active)
    return await create_subcategory_repo(subcategory, session)

async def get_subcategory(subcategory_id: str, session: AsyncSession):
    return await get_subcategory_by_id_repo(subcategory_id, session)

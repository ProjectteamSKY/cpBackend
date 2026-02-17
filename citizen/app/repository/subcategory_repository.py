from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import SubCategory as SubCategoryORM
from app.domain.subcategory_domain import SubCategory as SubCategoryDomain

async def create_subcategory_repo(subcategory: SubCategoryDomain, session: AsyncSession):
    orm = SubCategoryORM(id=subcategory.id, name=subcategory.name, description=subcategory.description,
                         category_id=subcategory.category_id, is_active=subcategory.is_active)
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return SubCategoryDomain(id=orm.id, name=orm.name, description=orm.description,
                             category_id=orm.category_id, is_active=orm.is_active)

async def get_subcategory_by_id_repo(subcategory_id: str, session: AsyncSession):
    result = await session.execute(select(SubCategoryORM).where(SubCategoryORM.id == subcategory_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return SubCategoryDomain(id=orm.id, name=orm.name, description=orm.description,
                             category_id=orm.category_id, is_active=orm.is_active)

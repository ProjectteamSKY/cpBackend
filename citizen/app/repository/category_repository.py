from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import Category as CategoryORM
from app.domain.category_domain import Category as CategoryDomain

async def create_category_repo(category: CategoryDomain, session: AsyncSession):
    orm = CategoryORM(id=category.id, name=category.name, description=category.description, is_active=category.is_active)
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return CategoryDomain(id=orm.id, name=orm.name, description=orm.description, is_active=orm.is_active)

async def get_category_by_id_repo(category_id: str, session: AsyncSession):
    result = await session.execute(select(CategoryORM).where(CategoryORM.id == category_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return CategoryDomain(id=orm.id, name=orm.name, description=orm.description, is_active=orm.is_active)

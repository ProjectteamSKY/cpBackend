from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import ProductType as ProductTypeORM
from app.domain.product_type_domain import ProductType as ProductTypeDomain

async def create_product_type_repo(pt: ProductTypeDomain, session: AsyncSession):
    orm = ProductTypeORM(id=pt.id, name=pt.name, description=pt.description)
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return ProductTypeDomain(id=orm.id, name=orm.name, description=orm.description)

async def get_product_type_by_id_repo(pt_id: str, session: AsyncSession):
    result = await session.execute(select(ProductTypeORM).where(ProductTypeORM.id == pt_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return ProductTypeDomain(id=orm.id, name=orm.name, description=orm.description)

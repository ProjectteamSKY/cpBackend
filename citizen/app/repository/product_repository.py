# app/repository/product_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models.product_models import Product as ProductORM
from app.domain.product_domain import Product as ProductDomain

# CREATE
async def create_product_repo(product: ProductDomain, session: AsyncSession) -> ProductDomain:
    orm = ProductORM(
        id=product.id,
        name=product.name,
        category_id=product.category_id,
        subcategory_id=product.subcategory_id,
        product_type_id=product.product_type_id,
        description=product.description,
        min_order_qty=product.min_order_qty,
        max_order_qty=product.max_order_qty,
        is_active=True
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return map_to_domain(orm)

# GET BY ID
async def get_product_by_id_repo(product_id: str, session: AsyncSession) -> ProductDomain | None:
    result = await session.execute(
        select(ProductORM)
        .where(ProductORM.id == product_id, ProductORM.is_active == True)
    )
    orm = result.scalar_one_or_none()
    return map_to_domain(orm) if orm else None

# GET ALL
async def get_all_products_repo(session: AsyncSession) -> list[ProductDomain]:
    result = await session.execute(
        select(ProductORM)
        .where(ProductORM.is_active == True)
        .order_by(ProductORM.created_at.desc())
    )
    return [map_to_domain(orm) for orm in result.scalars().all()]

# UPDATE
async def update_product_repo(product_id: str, data: dict, session: AsyncSession) -> ProductDomain | None:
    stmt = (
        update(ProductORM)
        .where(ProductORM.id == product_id, ProductORM.is_active == True)
        .values(**data, updated_at=datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )
    result = await session.execute(stmt)
    await session.commit()
    if result.rowcount == 0:
        return None
    return await get_product_by_id_repo(product_id, session)

# SOFT DELETE
async def delete_product_repo(product_id: str, session: AsyncSession) -> bool:
    stmt = (
        update(ProductORM)
        .where(ProductORM.id == product_id, ProductORM.is_active == True)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0

# MAP ORM -> DOMAIN
def map_to_domain(orm: ProductORM) -> ProductDomain:
    return ProductDomain(
        id=orm.id,
        name=orm.name,
        category_id=orm.category_id,
        subcategory_id=orm.subcategory_id,
        product_type_id=orm.product_type_id,
        description=orm.description,
        min_order_qty=orm.min_order_qty,
        max_order_qty=orm.max_order_qty,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

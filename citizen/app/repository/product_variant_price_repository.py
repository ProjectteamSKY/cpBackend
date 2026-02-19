# app/repository/product_variant_price_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models.product_models import ProductVariantPrice as PriceORM
from app.domain.product_variant_price_domain import ProductVariantPrice

# CREATE
async def create_price_repo(price: ProductVariantPrice, session: AsyncSession) -> ProductVariantPrice:
    orm = PriceORM(
        id=price.id,
        variant_id=price.variant_id,
        min_qty=price.min_qty,
        max_qty=price.max_qty,
        price=price.price,
        is_active=price.is_active
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return map_to_domain(orm)


# GET BY ID
async def get_price_by_id_repo(price_id: str, session: AsyncSession) -> ProductVariantPrice | None:
    result = await session.execute(
        select(PriceORM).where(PriceORM.id == price_id, PriceORM.is_active.in_([True, False]))
    )
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return map_to_domain(orm)


# GET ALL BY VARIANT
async def get_all_prices_by_variant_repo(variant_id: str, session: AsyncSession) -> list[ProductVariantPrice]:
    result = await session.execute(
        select(PriceORM).where(PriceORM.variant_id == variant_id, PriceORM.is_active == True)
    )
    return [map_to_domain(orm) for orm in result.scalars().all()]


# UPDATE
async def update_price_repo(price_id: str, data: dict, session: AsyncSession) -> ProductVariantPrice | None:
    stmt = (
        update(PriceORM)
        .where(PriceORM.id == price_id, PriceORM.is_active == True)
        .values(**data, updated_at=datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return None
    await session.commit()
    return await get_price_by_id_repo(price_id, session)


# SOFT DELETE
async def delete_price_repo(price_id: str, session: AsyncSession) -> bool:
    stmt = (
        update(PriceORM)
        .where(PriceORM.id == price_id, PriceORM.is_active == True)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0


# MAPPER
def map_to_domain(orm: PriceORM) -> ProductVariantPrice:
    return ProductVariantPrice(
        id=orm.id,
        variant_id=orm.variant_id,
        min_qty=orm.min_qty,
        max_qty=orm.max_qty,
        price=orm.price,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.db.models.product_models import ProductVariant as ProductVariantORM
from app.domain.product_variant_domain import ProductVariant

# CREATE
async def create_product_variant_repo(variant: ProductVariant, session: AsyncSession) -> ProductVariant:
    orm = ProductVariantORM(
        id=variant.id,
        product_id=variant.product_id,
        paper_type_id=variant.paper_type_id,
        finish_id=variant.finish_id,
        cut_type_id=variant.cut_type_id,
        shape_id=variant.shape_id,
        size_id=variant.size_id,
        sides=variant.sides,
        two_side_cut=variant.two_side_cut,
        four_side_cut=variant.four_side_cut,
        orientation=variant.orientation,
        is_active=variant.is_active
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return map_to_domain(orm)

# GET BY ID
async def get_product_variant_by_id_repo(variant_id: str, session: AsyncSession) -> ProductVariant | None:
    result = await session.execute(
        select(ProductVariantORM)
        .where(ProductVariantORM.id == variant_id, ProductVariantORM.is_active == True)
    )
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return map_to_domain(orm)

# GET ALL
async def get_all_product_variants_repo(session: AsyncSession) -> list[ProductVariant]:
    result = await session.execute(
        select(ProductVariantORM)
        .where(ProductVariantORM.is_active == True)
        .order_by(ProductVariantORM.created_at.desc())
    )
    return [map_to_domain(orm) for orm in result.scalars().all()]

# UPDATE
async def update_product_variant_repo(variant_id: str, data: dict, session: AsyncSession) -> ProductVariant | None:
    stmt = (
        update(ProductVariantORM)
        .where(ProductVariantORM.id == variant_id, ProductVariantORM.is_active == True)
        .values(**data, updated_at=datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return None
    await session.commit()
    return await get_product_variant_by_id_repo(variant_id, session)

# SOFT DELETE
async def delete_product_variant_repo(variant_id: str, session: AsyncSession) -> bool:
    stmt = (
        update(ProductVariantORM)
        .where(ProductVariantORM.id == variant_id, ProductVariantORM.is_active == True)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0

# MAPPER
def map_to_domain(orm: ProductVariantORM) -> ProductVariant:
    return ProductVariant(
        id=orm.id,
        product_id=orm.product_id,
        paper_type_id=orm.paper_type_id,
        finish_id=orm.finish_id,
        cut_type_id=orm.cut_type_id,
        shape_id=orm.shape_id,
        size_id=orm.size_id,
        sides=orm.sides,
        two_side_cut=orm.two_side_cut,
        four_side_cut=orm.four_side_cut,
        orientation=orm.orientation,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

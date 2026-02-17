from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import ProductVariant as ProductVariantORM
from app.domain.product_variant_domain import ProductVariant as ProductVariantDomain

async def create_product_variant_repo(variant: ProductVariantDomain, session: AsyncSession):
    orm = ProductVariantORM(
        id=variant.id,
        product_id=variant.product_id,
        paper_type_id=variant.paper_type_id,
        finish_id=variant.finish_id,
        cut_type_id=variant.cut_type_id,
        size=variant.size,
        sides=variant.sides,
        orientation=variant.orientation,
        price=variant.price,
        is_active=variant.is_active
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return ProductVariantDomain(
        id=orm.id,
        product_id=orm.product_id,
        paper_type_id=orm.paper_type_id,
        finish_id=orm.finish_id,
        cut_type_id=orm.cut_type_id,
        size=orm.size,
        sides=orm.sides,
        orientation=orm.orientation,
        price=orm.price,
        is_active=orm.is_active
    )

async def get_product_variant_by_id_repo(variant_id: str, session: AsyncSession):
    result = await session.execute(select(ProductVariantORM).where(ProductVariantORM.id == variant_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return ProductVariantDomain(
        id=orm.id,
        product_id=orm.product_id,
        paper_type_id=orm.paper_type_id,
        finish_id=orm.finish_id,
        cut_type_id=orm.cut_type_id,
        size=orm.size,
        sides=orm.sides,
        orientation=orm.orientation,
        price=orm.price,
        is_active=orm.is_active
    )

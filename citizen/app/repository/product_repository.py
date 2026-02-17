from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import Product as ProductORM, ProductVariant as VariantORM, ProductImage as ImageORM
from app.domain.product_domain import Product as ProductDomain
from app.domain.product_variant_domain import ProductVariant as VariantDomain
from app.domain.product_image_domain import ProductImage as ImageDomain

async def create_product_repo(product: ProductDomain, session: AsyncSession):
    orm = ProductORM(
        id=product.id, name=product.name, category_id=product.category_id,
        subcategory_id=product.subcategory_id, product_type_id=product.product_type_id,
        base_price=product.base_price, gst_percent=product.gst_percent, weight=product.weight,
        length=product.length, width=product.width, height=product.height,
        min_order_qty=product.min_order_qty, max_order_qty=product.max_order_qty,
        is_active=product.is_active
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return ProductDomain(
        id=orm.id, name=orm.name, category_id=orm.category_id, subcategory_id=orm.subcategory_id,
        product_type_id=orm.product_type_id, base_price=orm.base_price, gst_percent=orm.gst_percent,
        weight=orm.weight, length=orm.length, width=orm.width, height=orm.height,
        min_order_qty=orm.min_order_qty, max_order_qty=orm.max_order_qty, is_active=orm.is_active
    )

async def get_product_by_id_repo(product_id: str, session: AsyncSession):
    result = await session.execute(select(ProductORM).where(ProductORM.id == product_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return ProductDomain(
        id=orm.id, name=orm.name, category_id=orm.category_id, subcategory_id=orm.subcategory_id,
        product_type_id=orm.product_type_id, base_price=orm.base_price, gst_percent=orm.gst_percent,
        weight=orm.weight, length=orm.length, width=orm.width, height=orm.height,
        min_order_qty=orm.min_order_qty, max_order_qty=orm.max_order_qty, is_active=orm.is_active
    )

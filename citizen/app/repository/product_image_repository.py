from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import ProductImage as ProductImageORM
from app.domain.product_image_domain import ProductImage as ProductImageDomain

async def create_product_image_repo(image: ProductImageDomain, session: AsyncSession):
    orm = ProductImageORM(
        id=image.id,
        product_id=image.product_id,
        image_url=image.image_url,
        is_default=image.is_default
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return ProductImageDomain(
        id=orm.id,
        product_id=orm.product_id,
        image_url=orm.image_url,
        is_default=orm.is_default
    )

async def get_product_image_by_id_repo(image_id: str, session: AsyncSession):
    result = await session.execute(select(ProductImageORM).where(ProductImageORM.id == image_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return ProductImageDomain(
        id=orm.id,
        product_id=orm.product_id,
        image_url=orm.image_url,
        is_default=orm.is_default
    )

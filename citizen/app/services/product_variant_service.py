from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_variant_repository import create_product_variant_repo, get_product_variant_by_id_repo
from app.domain.product_variant_domain import ProductVariant as ProductVariantDomain

async def create_product_variant(data, session: AsyncSession):
    variant = ProductVariantDomain(
        product_id=data.product_id,
        paper_type_id=data.paper_type_id,
        finish_id=data.finish_id,
        cut_type_id=data.cut_type_id,
        size=data.size,
        sides=data.sides,
        orientation=data.orientation,
        price=data.price,
        is_active=data.is_active
    )
    return await create_product_variant_repo(variant, session)

async def get_product_variant(variant_id: str, session: AsyncSession):
    return await get_product_variant_by_id_repo(variant_id, session)

from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_repository import create_product_repo, get_product_by_id_repo
from app.domain.product_domain import Product as ProductDomain

async def create_product(data, session: AsyncSession):
    product = ProductDomain(
        name=data.name, category_id=data.category_id, subcategory_id=data.subcategory_id,
        product_type_id=data.product_type_id, base_price=data.base_price, gst_percent=data.gst_percent,
        weight=data.weight, length=data.length, width=data.width, height=data.height,
        min_order_qty=data.min_order_qty, max_order_qty=data.max_order_qty, is_active=data.is_active
    )
    return await create_product_repo(product, session)

async def get_product(product_id: str, session: AsyncSession):
    return await get_product_by_id_repo(product_id, session)

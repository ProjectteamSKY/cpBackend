from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_image_repository import create_product_image_repo, get_product_image_by_id_repo
from app.domain.product_image_domain import ProductImage as ProductImageDomain

async def create_product_image(data, session: AsyncSession):
    image = ProductImageDomain(
        product_id=data.product_id,
        image_url=data.image_url,
        is_default=data.is_default
    )
    return await create_product_image_repo(image, session)

async def get_product_image(image_id: str, session: AsyncSession):
    return await get_product_image_by_id_repo(image_id, session)

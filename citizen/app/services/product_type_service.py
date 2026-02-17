from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_type_repository import create_product_type_repo, get_product_type_by_id_repo
from app.domain.product_type_domain import ProductType as ProductTypeDomain

async def create_product_type(data, session: AsyncSession):
    pt = ProductTypeDomain(name=data.name, description=data.description)
    return await create_product_type_repo(pt, session)

async def get_product_type(pt_id: str, session: AsyncSession):
    return await get_product_type_by_id_repo(pt_id, session)

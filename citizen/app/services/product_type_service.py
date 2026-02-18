from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domain.product_type_domain import ProductType
from app.repository.product_type_repository import (
    create_product_type_repo,
    get_product_type_by_id_repo,
    get_all_product_types_repo,
    update_product_type_repo,
    delete_product_type_repo
)
from app.schemas.product_type_schema import ProductTypeCreateSchema

# Create
async def create_product_type(data: ProductTypeCreateSchema, session: AsyncSession) -> ProductType:
    product_type = ProductType(
        name=data.name,
        description=data.description
    )
    return await create_product_type_repo(product_type, session)

# Get single
async def get_product_type(product_type_id: str, session: AsyncSession) -> ProductType:
    product_type = await get_product_type_by_id_repo(product_type_id, session)
    if not product_type:
        raise HTTPException(404, "ProductType not found")
    return product_type

# Get all
async def get_all_product_types(session: AsyncSession) -> list[ProductType]:
    return await get_all_product_types_repo(session)

# Update
async def update_product_type(product_type_id: str, data: dict, session: AsyncSession) -> ProductType:
    updated = await update_product_type_repo(product_type_id, data, session)
    if not updated:
        raise HTTPException(404, "ProductType not found")
    return updated

# Soft delete
async def delete_product_type(product_type_id: str, session: AsyncSession) -> bool:
    success = await delete_product_type_repo(product_type_id, session)
    if not success:
        raise HTTPException(404, "ProductType not found")
    return success

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.product_type_domain import ProductType
from app.repository.product_type_repository import *

from app.schemas.product_type_schema import (
    ProductTypeCreateSchema,
    ProductTypeUpdateSchema
)


async def create_product_type(data, session: AsyncSession):

    try:
        pt = ProductType(
            name=data.name,
            description=data.description
        )

        return await create_product_type_repo(pt, session)

    except ValueError as e:
        raise HTTPException(400, str(e))


async def get_product_type(product_type_id: str, session: AsyncSession):

    pt = await get_product_type_by_id_repo(product_type_id, session)

    if not pt:
        raise HTTPException(404, "ProductType not found")

    return pt


async def get_all_product_types(session: AsyncSession):
    return await get_all_product_types_repo(session)


async def update_product_type(
    product_type_id: str,
    data: ProductTypeUpdateSchema,
    session: AsyncSession
):

    updated = await update_product_type_repo(
        product_type_id,
        data.model_dump(exclude_unset=True),
        session
    )

    if not updated:
        raise HTTPException(404, "ProductType not found")

    return updated


async def delete_product_type(product_type_id: str, session: AsyncSession):

    success = await delete_product_type_repo(product_type_id, session)

    if not success:
        raise HTTPException(404, "ProductType not found")

    return {"message": "ProductType deleted successfully"}

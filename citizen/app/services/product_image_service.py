# app/services/product_image_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domain.product_image_domain import ProductImage
from app.repository.product_image_repository import (
    create_product_image_repo,
    get_product_image_by_id_repo,
    get_all_images_by_product_repo,
    update_product_image_repo,
    delete_product_image_repo
)
from app.schemas.product_image_schema import ProductImageCreateSchema

# CREATE
async def create_product_image_service(
    data: ProductImageCreateSchema,
    file_path: str,
    session: AsyncSession,
    upload_folder: str
):
    img = ProductImage(
        product_id=data.product_id,
        image_url=file_path,
        is_default=data.is_default
    )
    return await create_product_image_repo(img, session, upload_folder)

# GET ONE
async def get_product_image_service(image_id: str, session: AsyncSession):
    img = await get_product_image_by_id_repo(image_id, session)
    if not img:
        raise HTTPException(404, "ProductImage not found")
    return img

# GET ALL FOR PRODUCT
async def get_all_images_by_product_service(product_id: str, session: AsyncSession):
    return await get_all_images_by_product_repo(product_id, session)

# UPDATE
async def update_product_image_service(image_id: str, data: dict, session: AsyncSession):
    updated = await update_product_image_repo(image_id, data, session)
    if not updated:
        raise HTTPException(404, "ProductImage not found")
    return updated

# DELETE
async def delete_product_image_service(image_id: str, session: AsyncSession):
    success = await delete_product_image_repo(image_id, session)
    if not success:
        raise HTTPException(404, "ProductImage not found")
    return {"message": "ProductImage deleted successfully"}


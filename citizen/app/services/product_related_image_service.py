# app/services/product_related_image_service.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.product_related_image_domain import ProductRelatedImageDomain
from app.repository.product_relatedimage_repository import (
    create_image_repo,
    create_multiple_images_repo,
    get_image_by_id_repo,
    get_all_images_by_product_repo,
    update_image_repo,
    delete_image_repo
)

# CREATE SINGLE
async def create_image_service(image: ProductRelatedImageDomain, session: AsyncSession, upload_folder: str):
    return await create_image_repo(image, session, upload_folder)

# CREATE MULTIPLE
async def create_bulk_images_service(product_id: str, file_paths: list[str], session: AsyncSession, upload_folder: str):
    images = [ProductRelatedImageDomain(product_id=product_id, image_url=path) for path in file_paths]
    return await create_multiple_images_repo(images, session, upload_folder)

# GET ONE
async def get_image_service(image_id: str, session: AsyncSession):
    img = await get_image_by_id_repo(image_id, session)
    if not img:
        raise HTTPException(404, "Image not found")
    return img

# GET ALL FOR PRODUCT
async def get_all_images_service(product_id: str, session: AsyncSession):
    return await get_all_images_by_product_repo(product_id, session)

# UPDATE
async def update_image_service(image_id: str, data: dict, session: AsyncSession):
    updated = await update_image_repo(image_id, data, session)
    if not updated:
        raise HTTPException(404, "Image not found")
    return updated

# DELETE
async def delete_image_service(image_id: str, session: AsyncSession):
    success = await delete_image_repo(image_id, session)
    if not success:
        raise HTTPException(404, "Image not found")
    return {"message": "Image deleted successfully"}
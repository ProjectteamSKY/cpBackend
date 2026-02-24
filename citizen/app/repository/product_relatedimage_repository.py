# app/repository/product_related_image_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
import os, shutil

from app.db.models.product_models import ProductRelatedImage as ProductRelatedImageORM
from app.domain.product_related_image_domain import ProductRelatedImageDomain

# CREATE SINGLE
async def create_image_repo(image: ProductRelatedImageDomain, session: AsyncSession, upload_folder: str):
    local_path = os.path.join(upload_folder, os.path.basename(image.image_url))
    shutil.move(image.image_url, local_path)
    image.image_url = local_path

    orm = ProductRelatedImageORM(
        id=image.id,
        product_id=image.product_id,
        image_url=image.image_url,
        is_default=image.is_default
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return map_to_domain(orm)

# CREATE MULTIPLE
async def create_multiple_images_repo(images: list[ProductRelatedImageDomain], session: AsyncSession, upload_folder: str):
    orm_objects = []
    for img in images:
        local_path = os.path.join(upload_folder, os.path.basename(img.image_url))
        shutil.move(img.image_url, local_path)
        img.image_url = local_path
        orm = ProductRelatedImageORM(
            id=img.id,
            product_id=img.product_id,
            image_url=img.image_url,
            is_default=img.is_default
        )
        session.add(orm)
        orm_objects.append(orm)
    await session.commit()
    for orm in orm_objects:
        await session.refresh(orm)
    return [map_to_domain(orm) for orm in orm_objects]

# GET BY ID
async def get_image_by_id_repo(image_id: str, session: AsyncSession):
    result = await session.execute(select(ProductRelatedImageORM).where(ProductRelatedImageORM.id == image_id))
    orm = result.scalar_one_or_none()
    return map_to_domain(orm) if orm else None

# GET ALL FOR PRODUCT
async def get_all_images_by_product_repo(product_id: str, session: AsyncSession):
    result = await session.execute(select(ProductRelatedImageORM).where(ProductRelatedImageORM.product_id == product_id))
    return [map_to_domain(orm) for orm in result.scalars().all()]

# UPDATE
async def update_image_repo(image_id: str, data: dict, session: AsyncSession):
    stmt = update(ProductRelatedImageORM).where(ProductRelatedImageORM.id == image_id).values(**data, updated_at=datetime.utcnow()).execution_options(synchronize_session="fetch")
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return None
    await session.commit()
    return await get_image_by_id_repo(image_id, session)

# DELETE
async def delete_image_repo(image_id: str, session: AsyncSession):
    stmt = delete(ProductRelatedImageORM).where(ProductRelatedImageORM.id == image_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0

# MAPPER
def map_to_domain(orm: ProductRelatedImageORM) -> ProductRelatedImageDomain:
    return ProductRelatedImageDomain(
        id=orm.id,
        product_id=orm.product_id,
        image_url=orm.image_url,
        is_default=orm.is_default,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )
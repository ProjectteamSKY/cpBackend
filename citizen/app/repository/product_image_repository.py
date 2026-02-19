# app/repository/product_image_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
import os
import shutil

from app.db.models.product_models import ProductImage as ProductImageORM
from app.domain.product_image_domain import ProductImage

# -------------------
# CREATE
# -------------------
async def create_product_image_repo(
    image: ProductImage,
    session: AsyncSession,
    upload_folder: str
) -> ProductImage:
    # Move file to local folder
    local_path = os.path.join(upload_folder, os.path.basename(image.image_url))
    shutil.move(image.image_url, local_path)
    image.image_url = local_path

    orm = ProductImageORM(
        id=image.id,
        product_id=image.product_id,
        image_url=image.image_url,
        is_default=image.is_default
    )

    session.add(orm)
    await session.commit()
    await session.refresh(orm)

    return map_to_domain(orm)

# -------------------
# GET BY ID
# -------------------
async def get_product_image_by_id_repo(
    image_id: str,
    session: AsyncSession
) -> ProductImage | None:
    result = await session.execute(
        select(ProductImageORM).where(ProductImageORM.id == image_id)
    )
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return map_to_domain(orm)

# -------------------
# GET ALL FOR PRODUCT
# -------------------
async def get_all_images_by_product_repo(
    product_id: str,
    session: AsyncSession
) -> list[ProductImage]:
    result = await session.execute(
        select(ProductImageORM).where(ProductImageORM.product_id == product_id)
    )
    return [map_to_domain(orm) for orm in result.scalars().all()]

# -------------------
# UPDATE
# -------------------
async def update_product_image_repo(
    image_id: str,
    data: dict,
    session: AsyncSession
) -> ProductImage | None:
    stmt = (
        update(ProductImageORM)
        .where(ProductImageORM.id == image_id)
        .values(**data, updated_at=datetime.utcnow())
        .execution_options(synchronize_session="fetch")
    )

    result = await session.execute(stmt)
    if result.rowcount == 0:
        return None

    await session.commit()
    return await get_product_image_by_id_repo(image_id, session)

# -------------------
# DELETE
# -------------------
async def delete_product_image_repo(
    image_id: str,
    session: AsyncSession
) -> bool:
    stmt = delete(ProductImageORM).where(ProductImageORM.id == image_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0



# -------------------
# MAPPER
# -------------------
def map_to_domain(orm: ProductImageORM) -> ProductImage:
    return ProductImage(
        id=orm.id,
        product_id=orm.product_id,
        image_url=orm.image_url,
        is_default=orm.is_default,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

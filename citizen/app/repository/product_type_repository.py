from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models.product_models import ProductType as ProductTypeORM
from app.domain.product_type_domain import ProductType


# Mapper
def map_to_domain(orm: ProductTypeORM) -> ProductType:
    return ProductType(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )


# CREATE
async def create_product_type_repo(
    product_type: ProductType,
    session: AsyncSession
) -> ProductType:

    # check duplicate
    result = await session.execute(
        select(ProductTypeORM).where(
            ProductTypeORM.name == product_type.name,
            ProductTypeORM.is_active == True
        )
    )

    if result.scalar_one_or_none():
        raise ValueError("ProductType with this name already exists")

    orm = ProductTypeORM(
        id=product_type.id,
        name=product_type.name,
        description=product_type.description,
        is_active=True
    )

    session.add(orm)

    await session.commit()
    await session.refresh(orm)

    return map_to_domain(orm)


# GET BY ID
async def get_product_type_by_id_repo(
    product_type_id: str,
    session: AsyncSession
) -> ProductType | None:

    result = await session.execute(
        select(ProductTypeORM).where(
            ProductTypeORM.id == product_type_id,
            ProductTypeORM.is_active == True
        )
    )

    orm = result.scalar_one_or_none()

    return map_to_domain(orm) if orm else None


# GET ALL
async def get_all_product_types_repo(
    session: AsyncSession
) -> list[ProductType]:

    result = await session.execute(
        select(ProductTypeORM)
        .order_by(ProductTypeORM.created_at.desc())
    )

    return [map_to_domain(orm) for orm in result.scalars().all()]


# UPDATE
async def update_product_type_repo(
    product_type_id: str,
    data: dict,
    session: AsyncSession
) -> ProductType | None:

    if not data:
        return await get_product_type_by_id_repo(product_type_id, session)

    stmt = (
        update(ProductTypeORM)
        .where(
            ProductTypeORM.id == product_type_id,
            ProductTypeORM.is_active == True
        )
        .values(
            **data,
            updated_at=datetime.utcnow()
        )
        .execution_options(synchronize_session="fetch")
    )

    result = await session.execute(stmt)

    if result.rowcount == 0:
        return None

    await session.commit()

    return await get_product_type_by_id_repo(product_type_id, session)


# SOFT DELETE
async def delete_product_type_repo(
    product_type_id: str,
    session: AsyncSession
) -> bool:

    stmt = (
        update(ProductTypeORM)
        .where(
            ProductTypeORM.id == product_type_id,
            ProductTypeORM.is_active == True
        )
        .values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
    )

    result = await session.execute(stmt)

    await session.commit()

    return result.rowcount > 0

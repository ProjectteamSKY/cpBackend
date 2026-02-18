from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.db.models.product_models import ProductType as ProductTypeORM
from app.domain.product_type_domain import ProductType

# Create
async def create_product_type_repo(product_type: ProductType, session: AsyncSession) -> ProductType:
    orm = ProductTypeORM(
        id=product_type.id,
        name=product_type.name,
        description=product_type.description,
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return ProductType(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# Get single
async def get_product_type_by_id_repo(product_type_id: str, session: AsyncSession) -> ProductType | None:
    result = await session.execute(select(ProductTypeORM).where(ProductTypeORM.id == product_type_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return ProductType(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# Get all
async def get_all_product_types_repo(session: AsyncSession) -> list[ProductType]:
    result = await session.execute(select(ProductTypeORM))
    return [
        ProductType(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
        for orm in result.scalars().all()
    ]

# Update
async def update_product_type_repo(product_type_id: str, data: dict, session: AsyncSession) -> ProductType | None:
    stmt = update(ProductTypeORM).where(ProductTypeORM.id == product_type_id).values(
        **data,
        updated_at=datetime.utcnow()
    ).execution_options(synchronize_session="fetch")
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return None
    await session.commit()
    return await get_product_type_by_id_repo(product_type_id, session)

# Soft delete
async def delete_product_type_repo(product_type_id: str, session: AsyncSession) -> bool:
    stmt = update(ProductTypeORM).where(ProductTypeORM.id == product_type_id).values(
        is_active=False,
        updated_at=datetime.utcnow()
    ).execution_options(synchronize_session="fetch")
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models.product_models import SubCategory as SubCategoryORM
from app.domain.subcategory_domain import SubCategory
from datetime import datetime

# Create
async def create_subcategory_repo(subcategory: SubCategory, session: AsyncSession) -> SubCategory:
    orm = SubCategoryORM(
        id=subcategory.id,
        name=subcategory.name,
        description=subcategory.description,
        category_id=subcategory.category_id,
        is_active=subcategory.is_active
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return SubCategory(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        category_id=orm.category_id,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# Get single
async def get_subcategory_by_id_repo(subcategory_id: str, session: AsyncSession) -> SubCategory | None:
    result = await session.execute(select(SubCategoryORM).where(SubCategoryORM.id == subcategory_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return SubCategory(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        category_id=orm.category_id,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# Get all
async def get_all_subcategories_repo(session: AsyncSession) -> list[SubCategory]:
    result = await session.execute(select(SubCategoryORM))
    return [
        SubCategory(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            category_id=orm.category_id,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
        for orm in result.scalars().all()
    ]

# Get only active
async def get_active_subcategories_repo(session: AsyncSession) -> list[SubCategory]:
    result = await session.execute(select(SubCategoryORM).where(SubCategoryORM.is_active == True))
    return [
        SubCategory(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            category_id=orm.category_id,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
        for orm in result.scalars().all()
    ]

# Get by category
async def get_subcategories_repo(session: AsyncSession, category_id: str | None = None) -> list[SubCategory]:
    query = select(SubCategoryORM)
    if category_id:
        query = query.where(SubCategoryORM.category_id == category_id)
    result = await session.execute(query)
    return [
        SubCategory(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            category_id=orm.category_id,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )
        for orm in result.scalars().all()
    ]

# Update
async def update_subcategory_repo(subcategory_id: str, data: dict, session: AsyncSession) -> SubCategory | None:
    stmt = update(SubCategoryORM).where(SubCategoryORM.id == subcategory_id).values(
        **data,
        updated_at=datetime.utcnow()
    ).execution_options(synchronize_session="fetch")
    result = await session.execute(stmt)
    if result.rowcount == 0:
        return None
    await session.commit()
    return await get_subcategory_by_id_repo(subcategory_id, session)

# Soft delete
async def delete_subcategory_repo(subcategory_id: str, session: AsyncSession) -> bool:
    stmt = update(SubCategoryORM).where(SubCategoryORM.id == subcategory_id).values(
        is_active=False,
        updated_at=datetime.utcnow()
    ).execution_options(synchronize_session="fetch")
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0

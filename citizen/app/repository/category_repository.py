import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import Category as CategoryORM
from app.domain.category_domain import Category as CategoryDomain
from fastapi import HTTPException


# CREATE
async def create_category_repo(category: CategoryDomain, session: AsyncSession):
    orm = CategoryORM(
        id=category.id,
        name=category.name,
        description=category.description,
        is_active=category.is_active
    )

    session.add(orm)
    await session.commit()
    await session.refresh(orm)

    return CategoryDomain(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active
    )


# GET ONE
async def get_category_by_id_repo(category_id: str, session: AsyncSession):
    result = await session.execute(
        select(CategoryORM).where(CategoryORM.id == category_id)  # compare string to string
    )
    orm = result.scalar_one_or_none()

    if not orm:
        return None

    return CategoryDomain(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active,
        created_at=orm.created_at,
        updated_at=orm.updated_at
    )

# GET ALL
async def get_all_categories_repo(session: AsyncSession):
    result = await session.execute(select(CategoryORM))
    categories = result.scalars().all()

    return [
        CategoryDomain(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            is_active=cat.is_active
        )
        for cat in categories
    ]


# UPDATE
async def update_category_repo(category: CategoryDomain, session: AsyncSession):
    result = await session.execute(
        select(CategoryORM).where(CategoryORM.id == category.id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        return None

    orm.name = category.name
    orm.description = category.description
    orm.is_active = category.is_active

    await session.commit()
    await session.refresh(orm)

    return CategoryDomain(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        is_active=orm.is_active
    )


# DELETE
# Soft delete
async def delete_category_repo(category_id: str, session: AsyncSession):
    result = await session.execute(
        select(CategoryORM).where(CategoryORM.id == category_id)
    )
    orm = result.scalar_one_or_none()

    if not orm:
        return False

    # Mark as inactive instead of deleting
    orm.is_active = False
    await session.commit()
    await session.refresh(orm)
    
    return True

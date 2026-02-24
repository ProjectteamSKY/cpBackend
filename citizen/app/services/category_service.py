from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.category_domain import Category
from app.utils.query_loader import load_queries


queries = load_queries()


# CREATE
async def create_category(category: Category, session: AsyncSession):

    await session.execute(
        text(queries["category"]["create"]),
        category.to_dict()
    )

    await session.commit()

    result = await session.execute(
        text(queries["category"]["get_by_id"]),
        {"id": category.id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# GET ALL
async def get_all_categories(session: AsyncSession):

    result = await session.execute(
        text(queries["category"]["get_all"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]


# GET BY ID
async def get_category_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["category"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# UPDATE
async def update_category(id: str, updates: dict, session: AsyncSession):

    set_clause = ", ".join(
        f"{key} = :{key}"
        for key in updates.keys()
    )

    await session.execute(
        text(
            queries["category"]["update"].format(
                set_clause=set_clause
            )
        ),
        {"id": id, **updates}
    )

    await session.commit()

    result = await session.execute(
        text(queries["category"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DELETE
async def delete_category(id: str, session: AsyncSession):

    existing = await session.execute(
        text(queries["category"]["get_by_id"]),
        {"id": id}
    )

    if not existing.fetchone():
        return None

    await session.execute(
        text(queries["category"]["delete"]),
        {"id": id}
    )

    await session.commit()

    return {"id": id}


# ACTIVATE
async def activate_category(id: str, session: AsyncSession):

    await session.execute(
        text(queries["category"]["activate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["category"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DEACTIVATE
async def deactivate_category(id: str, session: AsyncSession):

    await session.execute(
        text(queries["category"]["deactivate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["category"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.subcategory_domain import Subcategory
from app.utils.query_loader import load_queries


queries = load_queries()


# CREATE
async def create_subcategory(subcategory: Subcategory, session: AsyncSession):

    await session.execute(
        text(queries["subcategory"]["create"]),
        subcategory.to_dict()
    )

    await session.commit()

    result = await session.execute(
        text(queries["subcategory"]["get_by_id"]),
        {"id": subcategory.id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# GET ALL
async def get_all_subcategories(session: AsyncSession):

    result = await session.execute(
        text(queries["subcategory"]["get_all"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]


# GET BY ID
async def get_subcategory_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["subcategory"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# GET BY CATEGORY
async def get_subcategories_by_category(category_id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["subcategory"]["get_by_category"]),
        {"category_id": category_id}
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]


# UPDATE
async def update_subcategory(id: str, updates: dict, session: AsyncSession):

    set_clause = ", ".join(
        f"{key} = :{key}"
        for key in updates.keys()
    )

    await session.execute(
        text(
            queries["subcategory"]["update"].format(
                set_clause=set_clause
            )
        ),
        {"id": id, **updates}
    )

    await session.commit()

    result = await session.execute(
        text(queries["subcategory"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DELETE
async def delete_subcategory(id: str, session: AsyncSession):

    exists = await session.execute(
        text(queries["subcategory"]["get_by_id"]),
        {"id": id}
    )

    if not exists.fetchone():
        return None

    await session.execute(
        text(queries["subcategory"]["delete"]),
        {"id": id}
    )

    await session.commit()

    return {"id": id}


# ACTIVATE
async def activate_subcategory(id: str, session: AsyncSession):

    await session.execute(
        text(queries["subcategory"]["activate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["subcategory"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DEACTIVATE
async def deactivate_subcategory(id: str, session: AsyncSession):

    await session.execute(
        text(queries["subcategory"]["deactivate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["subcategory"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None
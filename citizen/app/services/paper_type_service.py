from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.paper_type_domain import PaperType
from app.utils.query_loader import load_queries


queries = load_queries()


# CREATE
async def create_paper_type(paper_type: PaperType, session: AsyncSession):

    await session.execute(
        text(queries["paper_type"]["create"]),
        paper_type.to_dict()
    )

    await session.commit()

    result = await session.execute(
        text(queries["paper_type"]["get_by_id"]),
        {"id": paper_type.id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# GET ALL
async def get_all_paper_types(session: AsyncSession):

    result = await session.execute(
        text(queries["paper_type"]["get_all"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]

async def get_all_paper_types_active(session: AsyncSession):

    result = await session.execute(
        text(queries["paper_type"]["get_all_active"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]


# GET BY ID
async def get_paper_type_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["paper_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# UPDATE
async def update_paper_type(id: str, updates: dict, session: AsyncSession):

    set_clause = ", ".join(
        f"{key} = :{key}"
        for key in updates.keys()
    )

    await session.execute(
        text(
            queries["paper_type"]["update"].format(
                set_clause=set_clause
            )
        ),
        {"id": id, **updates}
    )

    await session.commit()

    result = await session.execute(
        text(queries["paper_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# SOFT DELETE
async def delete_paper_type(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["paper_type"]["get_by_id"]),
        {"id": id}
    )

    if not result.fetchone():
        return None

    await session.execute(
        text(queries["paper_type"]["delete"]),
        {"id": id}
    )

    await session.commit()

    return {"id": id, "deleted": True}


# ACTIVATE
async def activate_paper_type(id: str, session: AsyncSession):

    await session.execute(
        text(queries["paper_type"]["activate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["paper_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DEACTIVATE
async def deactivate_paper_type(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["paper_type"]["deactivate"]),
        {"id": id}
    )

    # 🚀 Check if any row was updated
    if result.rowcount == 0:
        return None

    await session.commit()

    # Fetch updated record
    result = await session.execute(
        text(queries["paper_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None
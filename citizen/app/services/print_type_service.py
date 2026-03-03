from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.print_type_domain import PrintType
from app.utils.query_loader import load_queries


queries = load_queries()


# CREATE
async def create_print_type(print_type: PrintType, session: AsyncSession):

    await session.execute(
        text(queries["print_type"]["create"]),
        print_type.to_dict()
    )

    await session.commit()

    result = await session.execute(
        text(queries["print_type"]["get_by_id"]),
        {"id": print_type.id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# GET ALL
async def get_all_print_types(session: AsyncSession):

    result = await session.execute(
        text(queries["print_type"]["get_all"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]

async def get_all_print_types_active(session: AsyncSession):

    result = await session.execute(
        text(queries["print_type"]["get_all_active"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]


# GET BY ID
async def get_print_type_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["print_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# UPDATE
async def update_print_type(id: str, updates: dict, session: AsyncSession):

    set_clause = ", ".join(
        f"{key} = :{key}"
        for key in updates.keys()
    )

    await session.execute(
        text(
            queries["print_type"]["update"].format(
                set_clause=set_clause
            )
        ),
        {"id": id, **updates}
    )

    await session.commit()

    result = await session.execute(
        text(queries["print_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# SOFT DELETE
async def delete_print_type(id: str, session: AsyncSession):

    exists = await session.execute(
        text(queries["print_type"]["get_by_id"]),
        {"id": id}
    )

    if not exists.fetchone():
        return None

    await session.execute(
        text(queries["print_type"]["delete"]),
        {"id": id}
    )

    await session.commit()

    return {"id": id, "deleted": True}


# ACTIVATE
async def activate_print_type(id: str, session: AsyncSession):

    await session.execute(
        text(queries["print_type"]["activate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["print_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DEACTIVATE
async def deactivate_print_type(id: str, session: AsyncSession):

    await session.execute(
        text(queries["print_type"]["deactivate"]),
        {"id": id}
    )

    await session.commit()

    result = await session.execute(
        text(queries["print_type"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None
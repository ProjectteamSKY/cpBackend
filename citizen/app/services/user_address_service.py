from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user_address_domain import UserAddress
from app.utils.query_loader import load_queries

queries = load_queries()

# CREATE
async def create_user_address(address: UserAddress, session: AsyncSession):
    await session.execute(
        text(queries["user_address"]["create"]),
        address.to_dict()
    )
    await session.commit()
    result = await session.execute(
        text(queries["user_address"]["get_by_id"]),
        {"id": address.id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None

# GET ALL
async def get_all_addresses(user_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user_address"]["get_all"]),
        {"user_id": user_id}
    )
    return [dict(row._mapping) for row in result.fetchall()]

# GET BY ID
async def get_address_by_id(id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user_address"]["get_by_id"]),
        {"id": id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None

# UPDATE
async def update_user_address(id: str, updates: dict, session: AsyncSession):
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    await session.execute(
        text(queries["user_address"]["update"].format(set_clause=set_clause)),
        {"id": id, **updates}
    )
    await session.commit()
    return await get_address_by_id(id, session)

# DELETE
async def delete_user_address(id: str, session: AsyncSession):
    existing = await get_address_by_id(id, session)
    if not existing:
        return None
    await session.execute(text(queries["user_address"]["delete"]), {"id": id})
    await session.commit()
    return {"id": id}
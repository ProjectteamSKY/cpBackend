from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.order_domain import Order
from app.utils.query_loader import load_queries

queries = load_queries()

# CREATE
async def create_order(order: Order, session: AsyncSession):
    await session.execute(
        text(queries["order"]["create"]),
        order.to_dict()
    )
    await session.commit()
    result = await session.execute(
        text(queries["order"]["get_by_id"]),
        {"id": order.id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None

# GET ALL
async def get_all_orders(user_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["order"]["get_all"]),
        {"user_id": user_id}
    )
    return [dict(row._mapping) for row in result.fetchall()]

# GET BY ID
async def get_order_by_id(id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["order"]["get_by_id"]),
        {"id": id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None

# UPDATE
async def update_order(id: str, updates: dict, session: AsyncSession):
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    await session.execute(
        text(queries["order"]["update"].format(set_clause=set_clause)),
        {"id": id, **updates}
    )
    await session.commit()
    return await get_order_by_id(id, session)

# DELETE
async def delete_order(id: str, session: AsyncSession):
    existing = await get_order_by_id(id, session)
    if not existing:
        return None
    await session.execute(text(queries["order"]["delete"]), {"id": id})
    await session.commit()
    return {"id": id}
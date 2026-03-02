from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.order_item_domain import OrderItem
from app.utils.query_loader import load_queries

queries = load_queries()

# CREATE
async def create_order_item(order_item: OrderItem, session: AsyncSession):
    await session.execute(
        text(queries["order_item"]["create"]),
        order_item.to_dict()
    )
    await session.commit()
    return order_item.to_dict()

# GET ALL BY ORDER
async def get_items_by_order(order_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["order_item"]["get_all_by_order"]),
        {"order_id": order_id}
    )
    return [dict(row._mapping) for row in result.fetchall()]

# DELETE BY ORDER
async def delete_items_by_order(order_id: str, session: AsyncSession):
    await session.execute(
        text(queries["order_item"]["delete_by_order"]),
        {"order_id": order_id}
    )
    await session.commit()
    return {"order_id": order_id}
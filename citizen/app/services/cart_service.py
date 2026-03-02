from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.utils.query_loader import load_queries
from app.domain.cart_domain import Cart

queries = load_queries()


# ---------------- CREATE (Only one active cart allowed) ----------------
async def create_cart(cart: Cart, session: AsyncSession):

    # Check existing active cart
    result = await session.execute(
        text(queries["carts"]["get_active_by_user_id"]),
        {"user_id": cart.user_id}
    )
    existing = result.fetchone()

    if existing:
        return dict(existing._mapping)

    # Create new cart
    await session.execute(
        text(queries["carts"]["create"]),
        cart.to_dict()
    )
    await session.commit()

    return cart.to_dict()


# ---------------- GET ALL ----------------
async def get_all_carts(session: AsyncSession):
    result = await session.execute(
        text(queries["carts"]["get_all"])
    )
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]


# ---------------- GET BY ID ----------------
async def get_cart_by_id(cart_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["carts"]["get_by_id"]),
        {"id": cart_id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


# ---------------- GET ACTIVE BY USER ----------------
async def get_cart_by_user_id(user_id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["carts"]["get_active_by_user_id"]),
        {"user_id": user_id}
    )

    row = result.fetchone()
    return dict(row._mapping) if row else None


# ---------------- UPDATE ----------------
async def update_cart(cart_id: str, updates: dict, session: AsyncSession):

    # Build dynamic SET clause
    set_clause = ", ".join([f"{key} = :{key}" for key in updates.keys()])

    query = queries["carts"]["update"].replace("{set_clause}", set_clause)

    updates["id"] = cart_id

    await session.execute(text(query), updates)
    await session.commit()

    return await get_cart_by_id(cart_id, session)


# ---------------- DELETE ----------------
async def delete_cart(cart_id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["carts"]["delete"]),
        {"id": cart_id}
    )

    await session.commit()

    if result.rowcount == 0:
        return None

    return {"message": "Cart deleted successfully"}
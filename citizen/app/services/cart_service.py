from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.cart_domain import Cart
from app.utils.query_loader import load_queries

queries = load_queries()


# CREATE CART
async def create_cart(cart: Cart, session: AsyncSession):

    await session.execute(
        text(queries["carts"]["create"]),
        cart.to_dict()
    )

    await session.commit()

    result = await session.execute(
        text(queries["carts"]["get_by_id"]),
        {"id": cart.id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# GET ALL CARTS
async def get_all_carts(session: AsyncSession):

    result = await session.execute(
        text(queries["carts"]["get_all"])
    )

    return [
        dict(row._mapping)
        for row in result.fetchall()
    ]


# GET CART BY ID
async def get_cart_by_id(id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["carts"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# UPDATE CART
async def update_cart(id: str, updates: dict, session: AsyncSession):

    set_clause = ", ".join(
        f"{key} = :{key}"
        for key in updates.keys()
    )

    await session.execute(
        text(
            queries["carts"]["update"].format(
                set_clause=set_clause
            )
        ),
        {"id": id, **updates}
    )

    await session.commit()

    result = await session.execute(
        text(queries["carts"]["get_by_id"]),
        {"id": id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None


# DELETE CART
async def delete_cart(id: str, session: AsyncSession):

    existing = await session.execute(
        text(queries["carts"]["get_by_id"]),
        {"id": id}
    )

    if not existing.fetchone():
        return None

    await session.execute(
        text(queries["carts"]["delete"]),
        {"id": id}
    )

    await session.commit()

    return {"id": id}


async def get_cart_by_user_id(user_id: str, session: AsyncSession):

    result = await session.execute(
        text(queries["carts"]["get_by_user_id"]),
        {"user_id": user_id}
    )

    row = result.fetchone()

    return dict(row._mapping) if row else None
from fastapi import HTTPException
from app.utils.query_loader import load_queries
from app.domain.cart_domain import Cart
from app.core.database import execute, query, query_all

queries = load_queries()


# ---------------- CREATE (Only one active cart allowed) ----------------
async def create_cart(cart: Cart):

    # Check existing active cart
    existing = await query(
        queries["carts"]["get_active_by_user_id"],
        {"user_id": cart.user_id}
    )

    if existing:
        return dict(existing)

    # Create new cart
    await execute(
        queries["carts"]["create"],
        cart.to_dict()
    )

    return cart.to_dict()


# ---------------- GET ALL ----------------
async def get_all_carts():
    rows = await query_all(
        queries["carts"]["get_all"]
    )

    return [dict(row) for row in rows]


# ---------------- GET BY ID ----------------
async def get_cart_by_id(cart_id: str):
    row = await query(
        queries["carts"]["get_by_id"],
        {"id": cart_id}
    )

    return dict(row) if row else None


# ---------------- GET ACTIVE BY USER ----------------
async def get_cart_by_user_id(user_id: str):
    row = await query(
        queries["carts"]["get_active_by_user_id"],
        {"user_id": user_id}
    )

    return dict(row) if row else None


# ---------------- UPDATE ----------------
async def update_cart(cart_id: str, updates: dict):

    # Build dynamic SET clause
    set_clause = ", ".join([f"{key} = :{key}" for key in updates.keys()])

    query_string = queries["carts"]["update"].replace("{set_clause}", set_clause)

    updates["id"] = cart_id

    await execute(query_string, updates)

    return await get_cart_by_id(cart_id)


# ---------------- DELETE ----------------
async def delete_cart(cart_id: str):

    result = await execute(
        queries["carts"]["delete"],
        {"id": cart_id}
    )

    if result and result.rowcount == 0:
        return None

    return {"message": "Cart deleted successfully"}
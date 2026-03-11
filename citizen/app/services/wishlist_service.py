from fastapi import HTTPException
from app.domain.wishlist_domain import Wishlist
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


# -------------------------
# CREATE
# -------------------------
async def create_wishlist(wishlist: Wishlist):
    """
    Add product to user wishlist
    """
    # Check if already exists
    existing = await query(
        "SELECT * FROM wishlists WHERE user_id = :user_id AND product_id = :product_id",
        {"user_id": wishlist.user_id, "product_id": wishlist.product_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Product already in wishlist")

    await execute(queries["wishlist"]["create"], wishlist.to_dict())
    created = await query(queries["wishlist"]["get_by_id"], {"id": wishlist.id})
    return created


# -------------------------
# GET ALL
# -------------------------
async def get_all_wishlists():
    return await query_all(queries["wishlist"]["get_all"])


# -------------------------
# GET BY ID
# -------------------------
async def get_wishlist_by_id(id: str):
    return await query(queries["wishlist"]["get_by_id"], {"id": id})


# -------------------------
# GET BY USER
# -------------------------
async def get_wishlists_by_user(user_id: str):
    return await query_all(queries["wishlist"]["get_by_user"], {"user_id": user_id})


# -------------------------
# DELETE
# -------------------------
async def delete_wishlist(id: str):
    existing = await query(queries["wishlist"]["get_by_id"], {"id": id})
    if not existing:
        return None
    await execute(queries["wishlist"]["delete"], {"id": id})
    return {"id": id}
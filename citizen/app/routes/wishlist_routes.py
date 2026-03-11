from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.wishlist_domain import Wishlist
from app.services.wishlist_service import (
    create_wishlist,
    get_all_wishlists,
    get_wishlist_by_id,
    get_wishlists_by_user,
    delete_wishlist
)

router = APIRouter()

# --------------------------
# Pydantic Models
# --------------------------
class WishlistCreate(BaseModel):
    user_id: str
    product_id: str


# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_wishlist_endpoint(payload: WishlistCreate):
    wishlist = Wishlist(user_id=payload.user_id, product_id=payload.product_id)
    created = await create_wishlist(wishlist)
    return {"status": "success", "data": created}


# --------------------------
# LIST ALL
# --------------------------
@router.get("/list")
async def list_wishlists():
    wishlists = await get_all_wishlists()
    return {"status": "success", "wishlists": wishlists}


# --------------------------
# GET BY ID
# --------------------------
@router.get("/{id}")
async def get_wishlist_endpoint(id: str):
    wishlist = await get_wishlist_by_id(id)
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return {"status": "success", "data": wishlist}


# --------------------------
# GET BY USER
# --------------------------
@router.get("/user/{user_id}")
async def get_user_wishlist(user_id: str):
    items = await get_wishlists_by_user(user_id)
    return {"status": "success", "wishlists": items}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_wishlist_endpoint(id: str):
    result = await delete_wishlist(id)
    if not result:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    return {"status": "success", "deleted_id": id}
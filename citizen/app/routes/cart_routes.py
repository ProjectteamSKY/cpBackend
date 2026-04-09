from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.cart_domain import Cart
from app.services.cart_service import (
    create_cart,
    get_all_carts,
    get_cart_by_id,
    update_cart,
    delete_cart,
    get_cart_by_user_id
)

router = APIRouter()


# ---------------- SCHEMAS ----------------
class CartCreate(BaseModel):
    user_id: str
    status: Optional[str] = "active"
    total_amount: Optional[float] = 0
    total_discount: Optional[float] = 0


class CartUpdate(BaseModel):
    status: Optional[str] = None
    total_amount: Optional[float] = None
    total_discount: Optional[float] = None


# ---------------- CREATE ----------------
@router.post("/")
async def create_cart_endpoint(payload: CartCreate):
    cart = Cart(**payload.model_dump())
    return await create_cart(cart)


# ---------------- GET ALL ----------------
@router.get("/")
async def get_all_carts_endpoint():
    return await get_all_carts()


# ---------------- GET BY ID ----------------
@router.get("/{id}")
async def get_cart_endpoint(id: str):
    cart = await get_cart_by_id(id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


# ---------------- GET ACTIVE BY USER ----------------
@router.get("/user/{user_id}")
async def get_cart_by_user(user_id: str):
    cart = await get_cart_by_user_id(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Active cart not found")
    return cart


# ---------------- UPDATE ----------------
@router.put("/{id}")
async def update_cart_endpoint(id: str, payload: CartUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    cart = await update_cart(id, updates)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    return cart


# ---------------- DELETE ----------------
@router.delete("/{id}")
async def delete_cart_endpoint(id: str):
    result = await delete_cart(id)

    if not result:
        raise HTTPException(status_code=404, detail="Cart not found")

    return result
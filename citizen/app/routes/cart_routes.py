from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.cart_domain import Cart
from app.services.cart_service import create_cart, get_cart_by_id, update_cart, delete_cart,get_cart_by_user_id

router = APIRouter(prefix="/carts", tags=["Carts"])

# -------------------- Pydantic Schemas --------------------
class CartCreate(BaseModel):
    user_id: str
    status: Optional[str] = "active"
    total_amount: Optional[float] = 0
    total_discount: Optional[float] = 0

class CartUpdate(BaseModel):
    status: Optional[str] = None
    total_amount: Optional[float] = None
    total_discount: Optional[float] = None

# -------------------- Routes --------------------
@router.post("/")
async def create_cart_endpoint(payload: CartCreate, session: AsyncSession = Depends(get_session)):
    cart = Cart(**payload.model_dump())
    return await create_cart(cart, session)

@router.get("/{id}")
async def get_cart_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    cart = await get_cart_by_id(id, session)
    if not cart:
        raise HTTPException(404, "Cart not found")
    return cart

@router.put("/{id}")
async def update_cart_endpoint(id: str, payload: CartUpdate, session: AsyncSession = Depends(get_session)):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    cart = await update_cart(id, updates, session)
    if not cart:
        raise HTTPException(404, "Cart not found")
    return cart

@router.delete("/{id}")
async def delete_cart_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    result = await delete_cart(id, session)
    if not result:
        raise HTTPException(404, "Cart not found")
    return result

@router.get("/user/{user_id}")
async def get_cart_by_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    cart = await get_cart_by_user_id(user_id, session)

    if not cart:
        raise HTTPException(404, "Active cart not found")

    return cart
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.order_domain import Order
from app.services.orders_service import (
    create_order,
    get_all_orders,
    get_order_by_id,
    update_order,
    delete_order
)

router = APIRouter()

# Pydantic models
class OrderCreate(BaseModel):
    user_id: str
    cart_id: str
    total_amount: float
    address_id: Optional[str] = None
    status: Optional[str] = "pending"

class OrderUpdate(BaseModel):
    total_amount: Optional[float] = None
    address_id: Optional[str] = None
    status: Optional[str] = None

# CREATE
@router.post("/create")
async def create_order_endpoint(payload: OrderCreate, session: AsyncSession = Depends(get_session)):
    order = Order(**payload.model_dump())
    return await create_order(order, session)

# LIST
@router.get("/list/{user_id}")
async def list_orders(user_id: str, session: AsyncSession = Depends(get_session)):
    orders = await get_all_orders(user_id, session)
    return {"orders": orders}

# GET BY ID
@router.get("/{id}")
async def get_order(id: str, session: AsyncSession = Depends(get_session)):
    order = await get_order_by_id(id, session)
    if not order:
        raise HTTPException(404, "Order not found")
    return order

# UPDATE
@router.put("/{id}")
async def update_order_endpoint(id: str, payload: OrderUpdate, session: AsyncSession = Depends(get_session)):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    updated = await update_order(id, updates, session)
    if not updated:
        raise HTTPException(404, "Order not found")
    return {"status": "success", "data": updated}

# DELETE
@router.delete("/{id}")
async def delete_order_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    result = await delete_order(id, session)
    if not result:
        raise HTTPException(404, "Order not found")
    return {"status": "success", "deleted_id": id}
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.order_item_domain import OrderItem
from app.services.order_items_service import (
    create_order_item,
    get_items_by_order,
    delete_items_by_order
)

router = APIRouter()

# Pydantic models
class OrderItemCreate(BaseModel):
    order_id: str
    cart_item_id: str
    product_id: str
    variant_id: str
    quantity: int
    price: float
    total: float

# CREATE
@router.post("/create")
async def create_item(payload: OrderItemCreate, session: AsyncSession = Depends(get_session)):
    item = OrderItem(**payload.model_dump())
    return await create_order_item(item, session)

# LIST BY ORDER
@router.get("/list/{order_id}")
async def list_items(order_id: str, session: AsyncSession = Depends(get_session)):
    items = await get_items_by_order(order_id, session)
    return {"items": items}

# DELETE ALL ITEMS BY ORDER
@router.delete("/delete_by_order/{order_id}")
async def delete_items(order_id: str, session: AsyncSession = Depends(get_session)):
    result = await delete_items_by_order(order_id, session)
    return {"status": "success", "order_id": order_id}
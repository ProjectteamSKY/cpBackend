import json
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.cart_item_domain import CartItem
from app.services.cart_item_service import (
    create_cart_item_with_files,
    get_cart_items_by_cart_id,
    update_cart_item,
    delete_cart_item,
    get_cart_items_by_user_id
)

router = APIRouter(prefix="/cart-items", tags=["CartItems"])


class CartItemCreate(BaseModel):
    cart_id: str
    product_id: str
    variant_id: str
    quantity: int   
    selected_options: Optional[dict] = None


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    discount_id: Optional[str] = None
    selected_options: Optional[dict] = None


@router.post("/")
async def create_cart_item_endpoint(
    payload: CartItemCreate,
    session: AsyncSession = Depends(get_session)
):
    if payload.quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than zero")

    item = CartItem(
        cart_id=payload.cart_id,
        product_id=payload.product_id,
        variant_id=payload.variant_id,
        quantity=payload.quantity,
        unit_price=0,
        total_price=0,
        selected_options=payload.selected_options
    )

    return await create_cart_item(item, session)


@router.get("/{cart_id}")
async def get_cart_items(
    cart_id: str,
    session: AsyncSession = Depends(get_session)
):
    items = await get_cart_items_by_cart_id(cart_id, session)
    return {"items": items}


@router.put("/{id}")
async def update_cart_item_endpoint(
    id: str,
    payload: CartItemUpdate,
    session: AsyncSession = Depends(get_session)
):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No fields to update")

    item = await update_cart_item(id, updates, session)

    if not item:
        raise HTTPException(404, "Cart item not found")

    return item


@router.delete("/{id}")
async def delete_cart_item_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):
    result = await delete_cart_item(id, session)

    if not result:
        raise HTTPException(404, "Cart item not found")

    return result

@router.get("/user/{user_id}")
async def get_cart_items_by_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    items = await get_cart_items_by_user_id(user_id, session)

    return {"items": items}


@router.post("/with-files")
async def create_cart_item_with_files_endpoint(
    cart_id: str = Form(...),
    product_id: str = Form(...),
    variant_id: str = Form(...),
    quantity: int = Form(...),
    selected_options: str = Form("{}"),
    front_file: UploadFile | None = File(None),
    back_file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_session)
):

    item = CartItem(
        id=str(uuid.uuid4()),
        cart_id=cart_id,
        product_id=product_id,
        variant_id=variant_id,
        quantity=quantity,
        selected_options=json.loads(selected_options)
    )

    return await create_cart_item_with_files(
        item,
        front_file,
        back_file,
        session
    )
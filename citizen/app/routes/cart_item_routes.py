from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.cart_item_domain import CartItem
from app.services.cart_item_service import (
    create_cart_item,
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
    selected_options: Optional[dict] = None


# ✅ NORMAL CREATE (no files)
@router.post("/")
async def create_cart_item_endpoint(
    payload: CartItemCreate,
    session: AsyncSession = Depends(get_session)
):
    if payload.quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than zero")
    return await create_cart_item(payload, session)


# ✅ CREATE WITH FILES
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
    return await create_cart_item_with_files(
        cart_id,
        product_id,
        variant_id,
        quantity,
        selected_options,
        front_file,
        back_file,
        session
    )


@router.get("/cart/{cart_id}")
async def get_cart_items(cart_id: str, session: AsyncSession = Depends(get_session)):
    return await get_cart_items_by_cart_id(cart_id, session)


@router.get("/user/{user_id}")
async def get_cart_items_by_user(user_id: str, session: AsyncSession = Depends(get_session)):
    return await get_cart_items_by_user_id(user_id, session)


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
async def delete_cart_item_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    result = await delete_cart_item(id, session)
    if not result:
        raise HTTPException(404, "Cart item not found")
    return result

@router.get("/{cart_item_id}")
async def get_cart_item_by_id(cart_item_id: str, session: AsyncSession = Depends(get_session)):
    """Fetch a single cart item by its ID"""
    item = await session.get(CartItem, cart_item_id)
    if not item:
        raise HTTPException(404, "Cart item not found")
    return item
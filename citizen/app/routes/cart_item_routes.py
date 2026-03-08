from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.domain.cart_item_domain import CartItem
from app.services.cart_item_service import (
    create_cart_item,
    create_cart_item_with_files,
    get_cart_items_by_cart_id,
    get_cart_items_by_user_id,
    get_cart_item_by_id,
    update_cart_item,
    delete_cart_item
)

router = APIRouter(prefix="/cart-items", tags=["CartItems"])


# --------------------------
# Pydantic Models
# --------------------------
class CartItemCreate(BaseModel):
    cart_id: str
    product_id: str
    variant_id: str
    quantity: int
    selected_options: Optional[dict] = None


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    selected_options: Optional[dict] = None


# --------------------------
# CREATE
# --------------------------
@router.post("/")
async def create_cart_item_endpoint(payload: CartItemCreate):
    if payload.quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than zero")

    model = CartItem(**payload.model_dump())
    created = await create_cart_item(model)
    return {"status": "success", "data": created}


# --------------------------
# CREATE WITH FILES
# --------------------------
@router.post("/with-files")
async def create_cart_item_with_files_endpoint(
    cart_id: str = Form(...),
    product_id: str = Form(...),
    variant_id: str = Form(...),
    quantity: int = Form(...),
    product_variant_price_id: Optional[str] = Form(None),  # ✅ NEW
    customize_qty: Optional[int] = Form(None),              # ✅ NEW  
    selected_options: str = Form("{}"),                     # Position FIXED
    front_file: UploadFile | None = File(None),
    back_file: UploadFile | None = File(None),
):
    if quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than zero")
    
    result = await create_cart_item_with_files(
        cart_id, product_id, variant_id, quantity,
        product_variant_price_id, customize_qty, selected_options,
        front_file, back_file
    )
    return {"status": "success", "data": result}



# --------------------------
# LIST BY CART
# --------------------------
@router.get("/cart/{cart_id}")
async def get_by_cart(cart_id: str):
    items = await get_cart_items_by_cart_id(cart_id)
    return {"status": "success", "data": items}


# --------------------------
# LIST BY USER
# --------------------------
@router.get("/user/{user_id}")
async def get_by_user(user_id: str):
    items = await get_cart_items_by_user_id(user_id)
    return {"status": "success", "data": items}


# --------------------------
# GET SINGLE
# --------------------------
@router.get("/{id}")
async def get_single(id: str):
    item = await get_cart_item_by_id(id)
    if not item:
        raise HTTPException(404, "Cart item not found")

    return {"status": "success", "data": item}


# --------------------------
# UPDATE
# --------------------------
@router.put("/{id}")
async def update_endpoint(id: str, payload: CartItemUpdate):
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(400, "No fields to update")

    updated = await update_cart_item(id, update_data)

    if not updated:
        raise HTTPException(404, "Cart item not found")

    return {"status": "success", "data": updated}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_endpoint(id: str):
    deleted = await delete_cart_item(id)

    if not deleted:
        raise HTTPException(404, "Cart item not found")

    return {"status": "success", "deleted_id": id}
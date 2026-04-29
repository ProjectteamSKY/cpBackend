from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.orders_service import (
    checkout,
    get_order_by_id,
    update_order,
    delete_order,
    get_order_items,
    get_all_orders_tracking,
    update_order_status,
    get_user_orders,
    get_total_orders,
    get_total_orders_by_user,
    get_orders_summary,
    get_monthly_revenue,
    get_top_products,
    get_recent_orders,
    cancel_order
)
from app.core.database import query_all

router = APIRouter()


# -------------------------------
# Pydantic Models
# -------------------------------
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


class OrderItemResponse(BaseModel):
    id: str   # ✅ UUID
    product_id: str
    variant_id: str
    quantity: int
    unit_price: float
    total_price: float

class AddressResponse(BaseModel):
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None


class ShipmentResponse(BaseModel):
    awb_code: Optional[str] = None
    courier_name: Optional[str] = None
    freight_charges: Optional[float] = None
    tracking_url: Optional[str] = None
    label_url: Optional[str] = None
    pickup_status: Optional[str] = None
    current_status: Optional[str] = None
    delivered_at: Optional[str] = None


class OrderTrackingResponse(BaseModel):
    id: str
    status: str
    total_amount: float
    created_at: str
    updated_at: str
    user: UserResponse
    address: Optional[AddressResponse] = None
    items: List[OrderItemResponse] = []
    shipment: Optional[ShipmentResponse] = None


class CartItemPayload(BaseModel):
    cart_item_id: str
    product_variant_price_id: Optional[str] = None
    customize_qty: Optional[int] = None


class CheckoutRequest(BaseModel):
    user_id: str
    cart_id: str
    cart_items: List[CartItemPayload]
    address_id: str

    payment_method: Optional[str] = "COD"
    delivery_type: Optional[str] = "normal"
    courier_id: Optional[str] = None
    courier_name: Optional[str] = None
    delivery_charge: Optional[float] = 0


class OrderStatusUpdate(BaseModel):
    status: str


# CHECKOUT
@router.post("/checkout")
async def checkout_endpoint(payload: CheckoutRequest):
    try:
        cart_items_dicts = [item.model_dump(mode="json") for item in payload.cart_items]

        return await checkout(
            user_id=payload.user_id,
            cart_id=payload.cart_id,
            cart_items=cart_items_dicts,
            address_id=payload.address_id,

            payment_method=payload.payment_method,
            delivery_type=payload.delivery_type,
            courier_id=payload.courier_id,
            courier_name=payload.courier_name,
            delivery_charge=payload.delivery_charge
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# TRACKING / ADMIN VIEW
@router.get("/tracking", response_model=List[OrderTrackingResponse])
async def track_orders():
    orders = await get_all_orders_tracking()
    response = []

    for o in orders:
        # Correct JOIN query
        items_with_files = await query_all("""
            SELECT 
                oi.*, 
                oif.front_side_url, 
                oif.back_side_url, 
                oif.front_original_name,
                oif.back_original_name
            FROM order_items oi
            LEFT JOIN order_item_files oif 
                ON oi.id = oif.order_item_id
            WHERE oi.order_id = :order_id
            ORDER BY oi.id
        """, {"order_id": o["id"]})

        # Group items
        items_dict = {}

        for item in items_with_files:
            item_id = item["id"]

            if item_id not in items_dict:
                items_dict[item_id] = {
                    "id": item["id"],
                    "product_id": item["product_id"],
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],

                    # FIXED COLUMN NAMES
                    "unit_price": float(item["unit_price"]),
                    "total_price": float(item["total_price"]),

                    "files": []
                }

            #  Safe file handling
            if item.get("front_side_url") or item.get("back_side_url"):
                items_dict[item_id]["files"].append({
                    "front_side_url": item.get("front_side_url"),
                    "back_side_url": item.get("back_side_url"),
                    "front_original_name": item.get("front_original_name"),
                    "back_original_name": item.get("back_original_name"),
                })

        items_list = list(items_dict.values())

        # Final response
        response.append({
            "id": o["id"],
            "status": o["status"],
            "total_amount": float(o["total_amount"]),
            "created_at": str(o["created_at"]),
            "updated_at": str(o["updated_at"]),

            "user": {
                "id": o["user_id"],
                "username": o.get("username", "N/A"),
                "email": o.get("email"),
                "phone": o.get("phone") or o.get("user_phone"),
            },

            "address": (
                {
                    "address": o.get("address_line"),
                    "city": o.get("city"),
                    "state": o.get("state"),
                    "country": o.get("country"),
                    "postal_code": o.get("postal_code"),
                    "phone": o.get("phone") or o.get("address_phone"),
                }
                if o.get("address_line")
                else None
            ),

            "items": items_list,

            "shipment": (
                {
                    "awb_code": o.get("awb_code"),
                    "courier_name": o.get("courier_name"),
                    "freight_charges": float(o["freight_charges"]) if o.get("freight_charges") else None,
                    "tracking_url": o.get("tracking_url"),
                    "label_url": o.get("label_url"),
                    "current_status": o.get("current_status"),
                    "pickup_status": o.get("pickup_status"),
                    "delivered_at": str(o["delivered_at"]) if o.get("delivered_at") else None,
                }
                if o.get("awb_code")
                else None
            ),
        })

    return response

@router.get("/total")
async def total_orders():
    try:
        return await get_total_orders()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/total/{user_id}")
async def total_orders_by_user(user_id: str):
    try:
        return await get_total_orders_by_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary")
async def orders_summary():
    try:
        return await get_orders_summary()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/revenue/monthly")
async def monthly_revenue():
    try:
        return await get_monthly_revenue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/top-products")
async def top_products():
    try:
        return await get_top_products()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/recent-orders")
async def recent_orders():
    try:
        return await get_recent_orders()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}")
async def get_order(order_id: str):
    order = await get_order_by_id(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


# UPDATE ORDER STATUS
@router.put("/orders/{order_id}/status")
async def change_order_status(order_id: str, payload: OrderStatusUpdate):
    try:
        return await update_order_status(order_id, payload.status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# GET ORDER BY ID


# UPDATE ORDER
@router.put("/{order_id}")
async def update_order_endpoint(order_id: str, payload: OrderUpdate):
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    updated = await update_order(order_id, updates)
    if not updated:
        raise HTTPException(404, "Order not found")
    return {"status": "success", "data": updated}


# DELETE ORDER
@router.delete("/{order_id}")
async def delete_order_endpoint(order_id: str):
    result = await delete_order(order_id)
    if not result:
        raise HTTPException(404, "Order not found")
    return {"status": "success", "deleted_id": order_id}

@router.get("/list/{user_id}")
async def get_user_orders_endpoint(user_id: str):
    """Get all orders for a specific user"""
    try:
        orders = await get_user_orders(user_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/{order_id}/cancel")
async def cancel_order_endpoint(order_id: str):
    try:
        return await cancel_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
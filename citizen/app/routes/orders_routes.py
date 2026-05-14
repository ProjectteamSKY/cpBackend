import json
from typing import Any, Dict, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic import Field     

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
    cancel_order,
    get_sales_summary,
    get_sales_report,
    get_sales_by_status,
    get_monthly_sales_report,
    get_daily_sales,
    get_top_selling_products

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
    
class OrderItemFile(BaseModel):
    front_side_url: Optional[str] = None
    back_side_url: Optional[str] = None
    front_original_name: Optional[str] = None
    back_original_name: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: Optional[str] = None
    variant_id: str
    quantity: int
    unit_price: float
    total_price: float

    selected_attributes: List[Dict[str, Any]] = Field(default_factory=list)  # ✅
    files: List[OrderItemFile] = Field(default_factory=list)                # ✅

class AddressResponse(BaseModel):
    name: Optional[str] = None              # ✅ added
    address: str
    landmark: Optional[str] = None          # ✅ added
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: Optional[str] = None          # ✅ match API (you use name/full_name)
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

    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    delivery_type: Optional[str] = None

    total_amount: float
    delivery_charge: Optional[float] = 0

    created_at: str
    updated_at: str

    user: UserResponse
    address: Optional[AddressResponse] = None

    items: List[OrderItemResponse] = Field(default_factory=list)  # ✅

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

def normalize_selected_attributes(value):
    """
    Always returns List[Dict[str, Any]]
    Enforces consistent structure
    """
    try:
        if value is None:
            return []

        # string → JSON
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except:
                return []

        # dict → convert to list
        if isinstance(value, dict):
            return [
                {
                    "attribute_name": str(k),
                    "attribute_value_name": str(v)
                }
                for k, v in value.items()
            ]

        # list → normalize each item
        if isinstance(value, list):
            normalized = []

            for item in value:
                if not isinstance(item, dict):
                    continue

                # NEW FORMAT (correct)
                if "attribute_name" in item and "attribute_value_name" in item:
                    normalized.append({
                        "attribute_name": str(item.get("attribute_name")),
                        "attribute_value_name": str(item.get("attribute_value_name"))
                    })

                # OLD FORMAT (key/value)
                elif "key" in item and "value" in item:
                    normalized.append({
                        "attribute_name": str(item.get("key")),
                        "attribute_value_name": str(item.get("value"))
                    })

            return normalized

        return []

    except Exception:
        return []

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
        items_raw = await get_order_items(o["id"])
        items_dict = {}

        for item in items_raw:
            item_id = item["id"]

            # ✅ SAFE NORMALIZATION
            selected_attributes = normalize_selected_attributes(
                item.get("selected_attributes")
            )

            # ✅ GROUP ITEMS
            if item_id not in items_dict:
                items_dict[item_id] = {
                    "id": item["id"],
                    "product_id": item["product_id"],
                    "product_name": item.get("product_name"),
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],
                    "unit_price": float(item["unit_price"]),
                    "total_price": float(item["total_price"]),
                    "selected_attributes": selected_attributes if isinstance(selected_attributes, list) else [],
                    "files": []
                }

            # ✅ SAFE FILE HANDLING
            if any([
                item.get("front_side_url"),
                item.get("back_side_url"),
                item.get("front_original_name"),
                item.get("back_original_name")
            ]):
                items_dict[item_id]["files"].append({
                    "front_side_url": item.get("front_side_url"),
                    "back_side_url": item.get("back_side_url"),
                    "front_original_name": item.get("front_original_name"),
                    "back_original_name": item.get("back_original_name"),
                })

        # ✅ GUARANTEE LIST
        items_list = list(items_dict.values()) if items_dict else []

        response.append({
            "id": o["id"],
            "status": o["status"],
            "payment_method": o.get("payment_method"),
            "payment_status": o.get("payment_status"),
            "delivery_type": o.get("delivery_type"),

            "total_amount": float(o["total_amount"]),
            "delivery_charge": float(o.get("delivery_charge") or 0),

            "created_at": str(o["created_at"]),
            "updated_at": str(o["updated_at"]),

            "user": {
                "id": o["user_id"],
                "username": o.get("full_name"),
                "email": o.get("email"),
                "phone": o.get("user_phone"),
            },

            "address": (
                {
                    "name": None,
                    "address": o.get("address_line"),
                    "landmark": o.get("landmark"),
                    "city": o.get("city"),
                    "state": o.get("state"),
                    "country": o.get("country"),
                    "postal_code": o.get("postal_code"),
                    "phone": o.get("address_phone"),
                }
                if o.get("address_line")
                else None
            ),

            "items": items_list,  # ✅ ALWAYS LIST

            "shipment": (
                {
                    "awb_code": o.get("awb_code"),
                    "courier_name": o.get("shipment_courier"),
                    "freight_charges": float(o["freight_charges"]) if o.get("freight_charges") else None,
                    "tracking_url": o.get("tracking_url"),
                    "pickup_status": o.get("pickup_status"),
                    "current_status": o.get("current_status"),
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

# =========================================================
# SALES SUMMARY
# =========================================================
@router.get("/sales/summary")
async def sales_summary():
    try:
        return await get_sales_summary()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# SALES REPORT
# =========================================================
@router.get("/sales/report")
async def sales_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
):
    try:
        return await get_sales_report(
            start_date=start_date,
            end_date=end_date,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# SALES BY STATUS
# =========================================================
@router.get("/sales/status")
async def sales_by_status():
    try:
        return await get_sales_by_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# DAILY SALES
# =========================================================
@router.get("/sales/daily")
async def daily_sales():
    try:
        return await get_daily_sales()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# MONTHLY SALES
# =========================================================
@router.get("/sales/monthly")
async def monthly_sales():
    try:
        return await get_monthly_sales_report()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# TOP SELLING PRODUCTS
# =========================================================
@router.get("/sales/top-products")
async def top_selling_products():
    try:
        return await get_top_selling_products()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# from typing import Optional, List
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.database import get_session
# from app.domain.order_domain import Order
# from app.services.orders_service import (
#     checkout,
#     create_order,
#     get_all_orders,
#     get_order_by_id,
#     update_order,
#     delete_order,
#     get_order_items,
#     get_all_orders_tracking,
#     update_order_status
# )

# router = APIRouter()

# # Pydantic models
# class OrderCreate(BaseModel):
#     user_id: str
#     cart_id: str
#     total_amount: float
#     address_id: Optional[str] = None
#     status: Optional[str] = "pending"

# class OrderUpdate(BaseModel):
#     total_amount: Optional[float] = None
#     address_id: Optional[str] = None
#     status: Optional[str] = None
# # RESPONSE MODELS
# class OrderItemResponse(BaseModel):
#     id: int
#     product_id: str
#     variant_id: str
#     quantity: int
#     price: float
#     total: float

# class AddressResponse(BaseModel):
#     address: str
#     city: str | None
#     state: str | None
#     country: str | None
#     postal_code: str | None
#     phone: str | None

# class UserResponse(BaseModel):
#     id: str
#     username: str
#     email: str | None
#     phone: str | None

# class OrderTrackingResponse(BaseModel):
#     id: str
#     status: str
#     total_amount: float
#     created_at: str
#     updated_at: str
#     user: UserResponse
#     address: AddressResponse | None
#     items: List[OrderItemResponse] = []
# # CREATE
# @router.post("/create")
# async def create_order_endpoint(payload: OrderCreate, session: AsyncSession = Depends(get_session)):
#     order = Order(**payload.model_dump())
#     return await create_order(order, session)

# # LIST
# @router.get("/list/{user_id}")
# async def list_orders(user_id: str, session: AsyncSession = Depends(get_session)):
#     orders = await get_all_orders(user_id, session)
#     return {"orders": orders}

# # GET BY ID

# class CheckoutRequest(BaseModel):
#     user_id: str
#     cart_id: str
#     cart_item_ids: List[str]
#     address_id: str


# @router.post("/checkout")
# async def checkout_endpoint(
#     payload: CheckoutRequest,
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         return await checkout(
#             payload.user_id,
#             payload.cart_id,
#             payload.cart_item_ids,
#             payload.address_id,
#             session
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    

# # ROUTES
# @router.get("/tracking", response_model=List[OrderTrackingResponse])
# async def track_orders(session: AsyncSession = Depends(get_session)):

#     orders = await get_all_orders_tracking(session)

#     response = []
#     for o in orders:
#         items = await get_order_items(o["id"], session)

#         response.append({
#             "id": o["id"],
#             "status": o["status"],
#             "total_amount": float(o["total_amount"]),
#             "created_at": str(o["created_at"]),
#             "updated_at": str(o["updated_at"]),
#             "user": {
#                 "id": o["user_id"],
#                 "username": o["username"],
#                 "email": o.get("email"),
#                 "phone": o.get("user_phone")
#             },
#             "address": {
#                 "address": o.get("address_line"),
#                 "city": o.get("city"),
#                 "state": o.get("state"),
#                 "country": o.get("country"),
#                 "postal_code": o.get("postal_code"),
#                 "phone": o.get("address_phone")
#             } if o.get("address_line") else None,
#             "items": [
#                 {
#                     "id": i["id"],
#                     "product_id": i["product_id"],
#                     "variant_id": i["variant_id"],
#                     "quantity": i["quantity"],
#                     "price": float(i["price"]),
#                     "total": float(i["total"])
#                 } for i in items
#             ]
#         })

#     return response

# class OrderStatusUpdate(BaseModel):
#     status: str


# @router.put("/orders/{order_id}/status")
# async def change_order_status(
#     order_id: str,
#     payload: OrderStatusUpdate,
#     session: AsyncSession = Depends(get_session)
# ):
#     try:
#         return await update_order_status(
#             order_id,
#             payload.status,
#             session
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.get("/{id}")
# async def get_order(id: str, session: AsyncSession = Depends(get_session)):
#     order = await get_order_by_id(id, session)
#     if not order:
#         raise HTTPException(404, "Order not found")
#     return order

# # UPDATE
# @router.put("/{id}")
# async def update_order_endpoint(id: str, payload: OrderUpdate, session: AsyncSession = Depends(get_session)):
#     updates = payload.model_dump(exclude_unset=True)
#     if not updates:
#         raise HTTPException(400, "No fields to update")
#     updated = await update_order(id, updates, session)
#     if not updated:
#         raise HTTPException(404, "Order not found")
#     return {"status": "success", "data": updated}

# # DELETE
# @router.delete("/{id}")
# async def delete_order_endpoint(id: str, session: AsyncSession = Depends(get_session)):
#     result = await delete_order(id, session)
#     if not result:
#         raise HTTPException(404, "Order not found")
#     return {"status": "success", "deleted_id": id}


from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.orders_service import (
    checkout,
    create_order,
    get_all_orders,
    get_order_by_id,
    update_order,
    delete_order,
    get_order_items,
    get_all_orders_tracking,
    update_order_status
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

# RESPONSE MODELS
class OrderItemResponse(BaseModel):
    id: int
    product_id: str
    variant_id: str
    quantity: int
    price: float
    total: float

class AddressResponse(BaseModel):
    address: str
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    phone: str | None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str | None
    phone: str | None


class ShipmentResponse(BaseModel):
    awb_code: str | None = None
    courier_name: str | None = None
    freight_charges: float | None = None
    tracking_url: str | None = None
    label_url: str | None = None
    pickup_status: str | None = None
    current_status: str | None = None
    delivered_at: str | None = None


class OrderTrackingResponse(BaseModel):
    id: str
    status: str
    total_amount: float
    created_at: str
    updated_at: str
    user: UserResponse
    address: AddressResponse | None
    items: List[OrderItemResponse] = []
    shipment: ShipmentResponse | None = None

class CheckoutRequest(BaseModel):
    user_id: str
    cart_id: str
    cart_item_ids: List[str]
    address_id: str

class OrderStatusUpdate(BaseModel):
    status: str

# CREATE
@router.post("/create")
async def create_order_endpoint(payload: OrderCreate):
    order = {"user_id": payload.user_id, "cart_id": payload.cart_id, 
             "total_amount": payload.total_amount, "address_id": payload.address_id, 
             "status": payload.status}
    return await create_order(order)

# LIST
@router.get("/list/{user_id}")
async def list_orders(user_id: str):
    orders = await get_all_orders(user_id)
    return {"orders": orders}

# CHECKOUT
@router.post("/checkout")
async def checkout_endpoint(payload: CheckoutRequest):
    try:
        return await checkout(
            payload.user_id,
            payload.cart_id,
            payload.cart_item_ids,
            payload.address_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# TRACKING
@router.get("/tracking", response_model=List[OrderTrackingResponse])
async def track_orders():
    orders = await get_all_orders_tracking()
    response = []

    for o in orders:
        items = await get_order_items(o["id"])

        response.append({
            "id": o["id"],
            "status": o["status"],
            "total_amount": float(o["total_amount"]),
            "created_at": str(o["created_at"]),
            "updated_at": str(o["updated_at"]),

            "user": {
                "id": o["user_id"],
                "username": o["username"],
                "email": o.get("email"),
                "phone": o.get("user_phone")
            },

            "address": {
                "address": o.get("address_line"),
                "city": o.get("city"),
                "state": o.get("state"),
                "country": o.get("country"),
                "postal_code": o.get("postal_code"),
                "phone": o.get("address_phone")
            } if o.get("address_line") else None,

            "items": [
                {
                    "id": i["id"],
                    "product_id": i["product_id"],
                    "variant_id": i["variant_id"],
                    "quantity": i["quantity"],
                    "price": float(i["price"]),
                    "total": float(i["total"])
                }
                for i in items
            ],

            "shipment": {
                "awb_code": o.get("awb_code"),
                "courier_name": o.get("courier_name"),
                "freight_charges": float(o["freight_charges"]) if o.get("freight_charges") else None,
                "tracking_url": o.get("tracking_url"),
                "label_url": o.get("label_url"),
                "current_status": o.get("current_status"),
                "pickup_status": o.get("pickup_status"),
                "delivered_at": str(o["delivered_at"]) if o.get("delivered_at") else None
            } if o.get("awb_code") else None
        })

    return response

# UPDATE STATUS
@router.put("/orders/{order_id}/status")
async def change_order_status(order_id: str, payload: OrderStatusUpdate):
    try:
        return await update_order_status(order_id, payload.status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# GET BY ID
@router.get("/{id}")
async def get_order(id: str):
    order = await get_order_by_id(id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order

# UPDATE
@router.put("/{id}")
async def update_order_endpoint(id: str, payload: OrderUpdate):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    updated = await update_order(id, updates)
    if not updated:
        raise HTTPException(404, "Order not found")
    return {"status": "success", "data": updated}

# DELETE
@router.delete("/{id}")
async def delete_order_endpoint(id: str):
    result = await delete_order(id)
    if not result:
        raise HTTPException(404, "Order not found")
    return {"status": "success", "deleted_id": id}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_session
from app.services.shipping_service import (
    create_order_service,
    get_available_couriers_service,
    assign_courier_service,
    update_webhook_status_service,
    download_label_service,
    cancel_order_service,
    refund_order_service,
    couriers_service,
    hyperlocal_couriers_service,
    is_chennai_surrounding,
    get_wallet_balance_service,
    get_pickup_locations_service,
    get_manifest_label_service,
    get_invoice_service
)
from app.integrations.shiprocket_client import ShiprocketClient

router = APIRouter()

client = ShiprocketClient()

class CourierSelect(BaseModel):
    courier_id: int


class RefundRequest(BaseModel):
    amount: float = None  # optional, default full refund

@router.post("/create-order/{order_id}")
async def create_shiprocket_order(
    order_id: str,
):
    return await create_order_service(order_id)


@router.get("/couriers/{order_id}")
async def get_available_couriers(
    order_id: str,
):
    return await get_available_couriers_service(order_id)


@router.post("/assign-courier/{order_id}")
async def assign_courier(
    order_id: str,
    data: CourierSelect,
):
    return await assign_courier_service(order_id, data.courier_id)


@router.get("/label/{order_id}")
async def download_label(
    order_id: str,
):
    return await download_label_service(order_id)


@router.post("/webhook/shiprocket")
async def shiprocket_webhook(
    payload: dict,
):
    return await update_webhook_status_service(payload)


@router.post("/cancel-order/{order_id}")
async def cancel_order(
    order_id: str,
):
    return await cancel_order_service(order_id)


@router.post("/refund-order/{order_id}")
async def refund_order(
    order_id: str,
    data: RefundRequest,
):
    return await refund_order_service(order_id, data.amount)


@router.get("/track/{awb_code}")
async def track_awb(awb_code: str):
    """
    Track shipment using AWB code
    """
    try:
        return client.get_tracking(awb_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/serviceavailability")
async def get_available_couriers(
    pickup_postcode: str,
    delivery_postcode: str,
    weight: float,
    length: float,
    breadth: float,   # 👈 accept breadth
    height: float,
    declared_value: float,
    cod: int,
):
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@serviceavailability - shipping_router.py:107")

    return await couriers_service(
        pickup_postcode,
        delivery_postcode,
        weight,
        cod,
        declared_value,
        length,
        breadth,
        height
    )


@router.get("/hyperlocal/serviceability")
async def get_hyperlocal_couriers(
    pickup_postcode: str,
    delivery_postcode: str,
    cod: int,
):
    print("🔥 HYPERLOCAL SERVICEABILITY API CALLED - shipping_router.py:127")

    return await hyperlocal_couriers_service(
        pickup_postcode=pickup_postcode,
        delivery_postcode=delivery_postcode,
        cod=cod
    )

@router.get("/hyperlocal/check")
async def check_chennai_area(pincode: str):
    return await is_chennai_surrounding(pincode)    

@router.get("/wallet-balance")
async def get_wallet_balance():
    return await get_wallet_balance_service()


@router.get("/pickup-locations")
async def get_pickup_locations():
    return await get_pickup_locations_service()


@router.get("/manifest-label")
async def get_manifest_label(order_id: str):
    return await get_manifest_label_service(order_id)


@router.get("/invoice")
async def get_invoice(order_id: str):
    return await get_invoice_service(order_id)
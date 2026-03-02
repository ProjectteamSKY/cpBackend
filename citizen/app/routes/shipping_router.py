from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_session
from app.services.shipping_service import (
    create_order_service,
    get_available_couriers_service,
    assign_courier_service,
    update_webhook_status_service,
    download_label_service
)

router = APIRouter()


class CourierSelect(BaseModel):
    courier_id: int


@router.post("/create-order/{order_id}")
async def create_shiprocket_order(
    order_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await create_order_service(order_id, session)


@router.get("/couriers/{order_id}")
async def get_available_couriers(
    order_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await get_available_couriers_service(order_id, session)


@router.post("/assign-courier/{order_id}")
async def assign_courier(
    order_id: str,
    data: CourierSelect,
    session: AsyncSession = Depends(get_session)
):
    return await assign_courier_service(order_id, data.courier_id, session)


@router.get("/label/{order_id}")
async def download_label(
    order_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await download_label_service(order_id, session)


@router.post("/webhook/shiprocket")
async def shiprocket_webhook(
    payload: dict,
    session: AsyncSession = Depends(get_session)
):
    return await update_webhook_status_service(payload, session)
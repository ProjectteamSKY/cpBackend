from fastapi import APIRouter, Form, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.domain.product_discount_domain import ProductDiscount
from app.services.product_discount_service import (
    create_product_discount,
    get_all_product_discounts,
    get_product_discount_by_id,
    get_product_discounts_by_product,
    update_product_discount,
    delete_product_discount,
    activate_product_discount,
    deactivate_product_discount,
    get_product_discounts_by_date_range,
    get_all_product_discounts_active
)

router = APIRouter()


# ---------------- Pydantic Models ----------------

class ProductDiscountCreate(BaseModel):
    product_id: Optional[str]
    description: Optional[str]
    discount: str = "0%"
    start_date: datetime
    end_date: datetime


class ProductDiscountUpdate(BaseModel):
    product_id: Optional[str]
    description: Optional[str]
    discount: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ---------------- CREATE ----------------

@router.post("/create")
async def create_product_discount_endpoint(payload: ProductDiscountCreate):

    if payload.start_date > payload.end_date:
        raise HTTPException(400, "start_date cannot be after end_date")

    pd = ProductDiscount(**payload.dict())

    return await create_product_discount(pd)


# ---------------- GET ALL ----------------

@router.get("/list")
async def list_product_discounts():
    return {"discounts": await get_all_product_discounts()}


@router.get("/list/active")
async def list_product_discounts_active():
    return {"discounts": await get_all_product_discounts_active()}


# ---------------- GET BY ID ----------------

@router.get("/{id}")
async def get_product_discount_endpoint(id: str):
    discount = await get_product_discount_by_id(id)
    if not discount:
        raise HTTPException(404, "Product Discount not found")
    return discount


# ---------------- GET BY PRODUCT ----------------

@router.get("/product/{product_id}")
async def list_product_discounts_by_product(product_id: str):
    return {"discounts": await get_product_discounts_by_product(product_id)}


# ---------------- UPDATE ----------------

@router.put("/{id}")
async def update_product_discount_endpoint(
    id: str,
    product_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    discount: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
):
    existing = await get_product_discount_by_id(id)
    if not existing:
        raise HTTPException(404, "Product Discount not found")

    # Convert date strings manually
    parsed_start = datetime.fromisoformat(start_date) if start_date else existing["start_date"]
    parsed_end = datetime.fromisoformat(end_date) if end_date else existing["end_date"]

    if parsed_start > parsed_end:
        raise HTTPException(400, "start_date cannot be after end_date")

    pd = ProductDiscount(
        product_id=product_id or existing["product_id"],
        description=description or existing["description"],
        discount=discount or existing["discount"],
        start_date=parsed_start,
        end_date=parsed_end,
    )

    return await update_product_discount(id, pd)


# ---------------- SOFT DELETE ----------------

@router.delete("/{id}")
async def delete_product_discount_endpoint(id: str):
    return await delete_product_discount(id)


# ---------------- ACTIVATE ----------------

@router.put("/{id}/activate")
async def activate_product_discount_endpoint(id: str):
    return await activate_product_discount(id)


# ---------------- DEACTIVATE ----------------

@router.put("/{id}/deactivate")
async def deactivate_product_discount_endpoint(id: str):
    return await deactivate_product_discount(id)


# ---------------- DATE RANGE FILTER ----------------

@router.get("/by_date_range")
async def list_product_discounts_by_date_range(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...)
):
    if start_date > end_date:
        raise HTTPException(400, "start_date cannot be after end_date")

    discounts = await get_product_discounts_by_date_range(start_date, end_date)
    return {"discounts": discounts}
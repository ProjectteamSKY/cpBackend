from fastapi import APIRouter, Depends, Form, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from app.core.database import get_session
from app.domain.product_discount_domain import ProductDiscount
from app.services.product_discount_service import (
    create_product_discount,
    get_all_product_discounts,
    get_product_discount_by_id,
    get_product_discounts_by_product,
    update_product_discount,
    delete_product_discount,
    activate_product_discount,
    get_product_discounts_by_date_range,
    deactivate_product_discount,
    get_all_product_discounts_active
)

router = APIRouter()
class ProductDiscountCreate(BaseModel):
    product_id: Optional[str]
    description: Optional[str]
    discount: str = "0%"
    start_date: datetime
    end_date: datetime
# ---------------- CREATE ----------------
@router.post("/create")
async def create_product_discount_endpoint(
    payload: ProductDiscountCreate,
    session: AsyncSession = Depends(get_session)
):
    pd = ProductDiscount(
        product_id=payload.product_id,
        description=payload.description,
        discount=payload.discount,
        start_date=payload.start_date,
        end_date=payload.end_date
    )
    return await create_product_discount(pd, session)

# ---------------- GET ALL ----------------
@router.get("/list")
async def list_product_discounts(session: AsyncSession = Depends(get_session)):
    return {"discounts": await get_all_product_discounts(session)}


@router.get("/list/active")
async def list_product_discounts_active(session: AsyncSession = Depends(get_session)):
    return {"discounts": await get_all_product_discounts_active(session)}
# ---------------- GET BY ID ----------------
@router.get("/{id}")
async def get_product_discount_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    discount = await get_product_discount_by_id(id, session)
    if not discount:
        raise HTTPException(404, "Product Discount not found")
    return discount

# ---------------- GET BY PRODUCT ----------------
@router.get("/product/{product_id}")
async def list_product_discounts_by_product(product_id: str, session: AsyncSession = Depends(get_session)):
    return {"discounts": await get_product_discounts_by_product(product_id, session)}

# ---------------- UPDATE ----------------
@router.put("/{id}")
async def update_product_discount_endpoint(
    id: str,
    product_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    discount: str = Form("0%"),
    start_date: datetime = Form(..., description="Select start date (date picker)"),
    end_date: datetime = Form(..., description="Select end date (date picker)"),
    session: AsyncSession = Depends(get_session)
):
    pd = ProductDiscount(
        product_id=product_id,
        description=description,
        discount=discount,
        start_date=start_date,
        end_date=end_date
    )
    updated = await update_product_discount(id, pd, session)
    if not updated:
        raise HTTPException(404, "Product Discount not found")
    return updated

# ---------------- SOFT DELETE ----------------
@router.delete("/{id}")
async def delete_product_discount_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await delete_product_discount(id, session)

# ---------------- ACTIVATE ----------------
@router.put("/{id}/activate")
async def activate_product_discount_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await activate_product_discount(id, session)


# ---------------- DEACTIVATE ----------------
@router.put("/{id}/deactivate")
async def activate_product_discount_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await deactivate_product_discount(id, session)
# ---------------- DATE RANGE FILTER ----------------
@router.get("/by_date_range")
async def list_product_discounts_by_date_range(
    start_date: datetime = Query(..., description="Start date (date picker)"),
    end_date: datetime = Query(..., description="End date (date picker)"),
    session: AsyncSession = Depends(get_session)
):
    if start_date > end_date:
        raise HTTPException(400, "start_date cannot be after end_date")
    discounts = await get_product_discounts_by_date_range(start_date, end_date, session)
    return {"discounts": discounts}
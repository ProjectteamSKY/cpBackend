from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_session
from app.domain.product_variant_price_domain import ProductVariantPrice
from app.services.product_variant_price_service import (
    create_product_variant_price,
    get_all_product_variant_prices,
    get_product_variant_price_by_id,
    get_product_variant_prices_by_variant,
    update_product_variant_price,
    soft_delete_product_variant_price,
    activate_product_variant_price,
    deactivate_product_variant_price
)

router = APIRouter()

# ---------------- CREATE ----------------
@router.post("/create")
async def create_pvp_endpoint(
    variant_id: str = Form(...),
    min_qty: int = Form(...),
    price: float = Form(...),
    discount_id: Optional[str] = Form(None),
    is_active: bool = Form(True),
    session: AsyncSession = Depends(get_session)
):
    pvp = ProductVariantPrice(
        variant_id=variant_id,
        min_qty=min_qty,
        price=price,
        discount_id=discount_id,
        is_active=is_active
    )
    return await create_product_variant_price(pvp, session)

# ---------------- GET ALL ----------------
@router.get("/list")
async def list_pvp(session: AsyncSession = Depends(get_session)):
    prices = await get_all_product_variant_prices(session)
    return {"prices": prices}

# ---------------- GET BY ID ----------------
@router.get("/{id}")
async def get_pvp(id: str, session: AsyncSession = Depends(get_session)):
    pvp = await get_product_variant_price_by_id(id, session)
    if not pvp:
        raise HTTPException(404, "Product Variant Price not found")
    return pvp

# ---------------- GET BY VARIANT ----------------
@router.get("/variant/{variant_id}")
async def list_pvp_by_variant(variant_id: str, session: AsyncSession = Depends(get_session)):
    return {"prices": await get_product_variant_prices_by_variant(variant_id, session)}

# ---------------- UPDATE ----------------
@router.put("/{id}")
async def update_pvp_endpoint(
    id: str,
    min_qty: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    discount_id: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    updates = {}
    if min_qty is not None: updates["min_qty"] = min_qty
    if price is not None: updates["price"] = price
    if discount_id is not None: updates["discount_id"] = discount_id
    if is_active is not None: updates["is_active"] = is_active

    if not updates:
        raise HTTPException(400, "No fields to update")

    return await update_product_variant_price(id, updates, session)

# ---------------- SOFT DELETE ----------------
@router.delete("/{id}")
async def soft_delete_pvp_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    return await soft_delete_product_variant_price(id, session)

# ---------------- ACTIVATE ----------------
@router.put("/{id}/activate")
async def activate_pvp_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await activate_product_variant_price(id, session)


@router.put("/{id}/deactivate")
async def deactivate_pvp_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await deactivate_product_variant_price(id, session)
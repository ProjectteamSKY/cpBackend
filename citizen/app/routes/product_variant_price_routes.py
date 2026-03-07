from fastapi import APIRouter, Form, HTTPException
from typing import Optional

from app.domain.product_variant_price_domain import ProductVariantPrice
from app.services.product_variant_price_service import (
    create_product_variant_price,
    get_all_product_variant_prices,
    get_product_variant_price_by_id,
    get_product_variant_prices_by_variant,
    update_product_variant_price,
    soft_delete_product_variant_price,
    activate_product_variant_price,
    deactivate_product_variant_price,
    get_variant_with_paper_and_size
)
from app.services.product_variant_service import calculate_variant_weight

router = APIRouter()


# ---------------- CREATE ----------------
@router.post("/create")
async def create_pvp_endpoint(
    variant_id: str = Form(...),
    min_qty: int = Form(...),
    price: float = Form(...),
    discount_id: Optional[str] = Form(None),
    is_active: bool = Form(True),
):
    pvp = ProductVariantPrice(
        variant_id=variant_id,
        min_qty=min_qty,
        price=price,
        discount_id=discount_id,
        is_active=is_active
    )

    return await create_product_variant_price(pvp)


# ---------------- GET ALL ----------------
@router.get("/list")
async def list_pvp():
    prices = await get_all_product_variant_prices()
    return {"prices": prices}


# ---------------- GET BY ID ----------------
@router.get("/{id}")
async def get_pvp(id: str):
    pvp = await get_product_variant_price_by_id(id)
    if not pvp:
        raise HTTPException(404, "Product Variant Price not found")
    return pvp


# ---------------- GET BY VARIANT ----------------
@router.get("/variant/{variant_id}")
async def list_pvp_by_variant(variant_id: str):
    return {"prices": await get_product_variant_prices_by_variant(variant_id)}


# ---------------- UPDATE ----------------
@router.put("/{id}")
async def update_pvp_endpoint(
    id: str,
    min_qty: Optional[int] = Form(None),
    price: Optional[float] = Form(None),
    discount_id: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
):

    updates = {}

    if min_qty is not None:
        updates["min_qty"] = min_qty
    if price is not None:
        updates["price"] = price
    if discount_id is not None:
        updates["discount_id"] = discount_id
    if is_active is not None:
        updates["is_active"] = is_active

    if not updates:
        raise HTTPException(400, "No fields to update")

    result = await update_product_variant_price(id, updates)

    if not result:
        raise HTTPException(404, "Product Variant Price not found")

    return result


# ---------------- SOFT DELETE ----------------
@router.delete("/{id}")
async def soft_delete_pvp_endpoint(id: str):
    return await soft_delete_product_variant_price(id)


# ---------------- ACTIVATE ----------------
@router.put("/{id}/activate")
async def activate_pvp_endpoint(id: str):
    return await activate_product_variant_price(id)


@router.put("/{id}/deactivate")
async def deactivate_pvp_endpoint(id: str):
    return await deactivate_product_variant_price(id)


@router.get("/variant/{variant_id}/price-weight/{price_id}")
async def get_price_weight_by_price_id(variant_id: str, price_id: str):
    """
    Calculate total weight and total price based on selected product_variant_price ID.
    """

    # 1️⃣ Fetch the variant details (width, height, gsm)
    variant = await get_variant_with_paper_and_size(variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Product variant not found")

    # 2️⃣ Fetch all prices for this variant
    prices = await get_product_variant_prices_by_variant(variant_id)
    if not prices:
        raise HTTPException(status_code=404, detail="No prices found for this variant")

    # 3️⃣ Find the selected price tier by price_id
    selected_price = next((p for p in prices if p["id"] == price_id), None)
    if not selected_price:
        raise HTTPException(status_code=404, detail="Price ID not found")

    # 4️⃣ Get quantity from the selected price tier's min_qty
    quantity = selected_price["min_qty"]

    # 5️⃣ Calculate weight
    width_m = variant["width"] / 1000   # mm → meters
    height_m = variant["height"] / 1000
    area_m2 = width_m * height_m
    gsm = variant.get("gsm") or 300
    total_weight_grams = area_m2 * gsm * quantity

    # 6️⃣ Calculate total price
    total_price = selected_price["price"] * quantity

    # 7️⃣ Return response
    return {
        "variant_id": variant_id,
        "price_id": price_id,
        "quantity": quantity,
        "unit_price": selected_price["price"],
        "total_price": round(total_price, 2),
        "total_weight_grams": round(total_weight_grams, 2)
    }
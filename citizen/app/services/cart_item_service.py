import json
import uuid
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException, UploadFile

from app.core.database import execute, query, query_all
from app.utils.query_loader import load_queries

queries = load_queries()

UPLOAD_FOLDER = "media/cart_items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# FILE UPLOAD
# =========================================================
def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return path.replace("\\", "/")


# =========================================================
# PRICE LOOKUP
# =========================================================
async def get_variant_price(variant_id: str, quantity: int):
    row = await query(
        queries["cart_items"]["variant_price_lookup"],
        {"variant_id": variant_id, "quantity": quantity},
    )

    if not row:
        raise HTTPException(400, "No valid price found for this quantity")

    return row


# =========================================================
# RECALCULATE CART
# =========================================================
async def recalculate_cart(cart_id: str):
    result = await query(
        queries["cart_items"]["cart_total"],
        {"cart_id": cart_id},
    )

    total = result["total"] if result else 0

    await execute(
        queries["cart_items"]["update_cart_total"],
        {
            "total": total,
            "cart_id": cart_id,
            "updated_at": datetime.utcnow()
        },
    )


# =========================================================
# CREATE / MERGE CART ITEM
# =========================================================
async def create_cart_item(payload: Any):

    # =====================================================
    # FETCH PRICE
    # =====================================================
    price = await get_variant_price(
        payload.variant_id,
        payload.quantity
    )

    # =====================================================
    # SAFE OPTIONAL VALUES
    # =====================================================
    design_request_id = getattr(
        payload,
        "design_request_id",
        None
    )

    design_price = getattr(
        payload,
        "design_price",
        None
    )

    # =====================================================
    # TOTALS
    # =====================================================
    product_total = (
        float(price["price"]) * payload.quantity
    )

    final_total = product_total + (
        float(design_price)
        if design_price is not None
        else 0
    )

    # =====================================================
    # CHECK EXISTING
    # =====================================================
    existing = await query(
        queries["cart_items"]["find_existing_item"],
        {
            "cart_id": payload.cart_id,
            "variant_id": payload.variant_id
        },
    )

    # =====================================================
    # MERGE EXISTING
    # =====================================================
    if existing:

        new_qty = (
            existing["quantity"] + payload.quantity
        )

        new_price = await get_variant_price(
            payload.variant_id,
            new_qty
        )

        merged_product_total = (
            float(new_price["price"]) * new_qty
        )

        merged_total = merged_product_total + (
            float(design_price)
            if design_price is not None
            else 0
        )

        await execute(
            queries["cart_items"]["merge_update"],
            {
                "id": existing["id"],

                "quantity": new_qty,

                "unit_price": new_price["price"],

                "total_price": merged_total,

                "design_request_id": design_request_id,

                "design_price": design_price,

                "discount_id": new_price.get(
                    "discount_id"
                ),

                "updated_at": datetime.utcnow()
            },
        )

        await recalculate_cart(payload.cart_id)

        return {
            "status": "success",
            "message": "Item merged",
            "id": existing["id"]
        }

    # =====================================================
    # CREATE NEW ITEM
    # =====================================================
    item_id = str(uuid.uuid4())

    await execute(
        queries["cart_items"]["create"],
        {
            "id": item_id,

            "cart_id": payload.cart_id,

            "product_id": payload.product_id,

            "variant_id": payload.variant_id,

            "variant_price_id": price["id"],

            "design_request_id": design_request_id,

            "quantity": payload.quantity,

            "unit_price": price["price"],

            "total_price": final_total,

            "design_price": design_price,

            "discount_id": price.get(
                "discount_id"
            ),

            "selected_attributes": json.dumps(
                getattr(
                    payload,
                    "selected_attributes",
                    {}
                )
            ),

            "created_at": datetime.utcnow(),

            "updated_at": datetime.utcnow(),
        },
    )

    await recalculate_cart(payload.cart_id)

    return {
        "status": "success",
        "message": "Item added",
        "id": item_id
    }


# =========================================================
# CREATE WITHOUT FILES (FINAL FIXED)
# =========================================================
async def create_cart_item_with_out_files(
    cart_id: str,
    product_id: str,
    variant_id: str,
    quantity: int,
    selected_attributes: str = "{}",
):
    if quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than 0")

    try:
        selected_attributes_dict = json.loads(selected_attributes or "{}")
    except Exception:
        raise HTTPException(400, "Invalid selected_attributes JSON")

    price = await get_variant_price(variant_id, quantity)

    existing = await query(
        queries["cart_items"]["find_existing_item"],
        {
            "cart_id": cart_id,
            "variant_id": variant_id
        },
    )

    # -------------------------
    # MERGE
    # -------------------------
    if existing:
        new_qty = existing["quantity"] + quantity
        new_price = await get_variant_price(variant_id, new_qty)

        await execute(
            queries["cart_items"]["merge_update"],
            {
                "id": existing["id"],
                "quantity": new_qty,
                "unit_price": new_price["price"],
                "total_price": new_price["price"] * new_qty,
                "discount_id": new_price.get("discount_id"),
                "updated_at": datetime.utcnow(),
            },
        )

        await recalculate_cart(cart_id)

        return {
            "status": "success",
            "message": "Item merged",
            "id": existing["id"]
        }

    # -------------------------
    # CREATE
    # -------------------------
    item_id = str(uuid.uuid4())

    await execute(
        queries["cart_items"]["create"],
        {
            "id": item_id,
            "cart_id": cart_id,
            "product_id": product_id,
            "variant_id": variant_id,
            "variant_price_id": price["id"],
            "quantity": quantity,
            "unit_price": price["price"],
            "total_price": price["price"] * quantity,
            "discount_id": price.get("discount_id"),
            "selected_attributes": json.dumps(selected_attributes_dict),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    )

    await recalculate_cart(cart_id)

    return {
        "status": "success",
        "message": "Item added",
        "id": item_id
    }


# =========================================================
# CREATE WITH FILES
# =========================================================
async def create_cart_item_with_files(
    cart_id,
    product_id,
    variant_id,
    quantity,
    selected_attributes,
    front_file,
    back_file
):
    class Payload: pass

    payload = Payload()
    payload.cart_id = cart_id
    payload.product_id = product_id
    payload.variant_id = variant_id
    payload.quantity = quantity
    payload.selected_attributes = json.loads(selected_attributes or "{}")

    result = await create_cart_item(payload)

    if "id" in result and (front_file or back_file):
        item_id = result["id"]

        front_url = save_upload(front_file) if front_file else None
        back_url = save_upload(back_file) if back_file else None

        await execute(
            queries["cart_items"]["insert_cart_files"],
            {
                "id": str(uuid.uuid4()),
                "cart_item_id": item_id,
                "front_side_url": front_url,
                "back_side_url": back_url,
                "front_original_name": front_file.filename if front_file else None,
                "back_original_name": back_file.filename if back_file else None,
            }
        )

    return result


# =========================================================
# GET METHODS
# =========================================================
async def get_cart_items_by_cart_id(cart_id: str):
    return await query_all(
        queries["cart_items"]["get_by_cart_id"],
        {"cart_id": cart_id}
    )


async def get_cart_items_by_user_id(user_id: str) -> List[Dict]:
    items = await query_all(
        queries["cart_items"]["get_by_user_id"],
        {"user_id": user_id}
    )

    for item in items:
        item["files"] = await query_all(
            queries["cart_items"]["get_files_by_cart_item_id"],
            {"cart_item_id": item["id"]}
        )

    return items


async def get_cart_item_by_id(id: str):
    return await query(
        queries["cart_items"]["get_by_id"],
        {"id": id}
    )


# =========================================================
# UPDATE
# =========================================================
async def update_cart_item(id: str, updates: dict):
    existing = await get_cart_item_by_id(id)
    if not existing:
        return None

    if "quantity" in updates:
        price = await get_variant_price(
            existing["variant_id"],
            updates["quantity"]
        )

        updates["unit_price"] = price["price"]
        updates["total_price"] = price["price"] * updates["quantity"]
        updates["discount_id"] = price.get("discount_id")

    if "selected_attributes" in updates:
        updates["selected_attributes"] = json.dumps(updates["selected_attributes"])

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())

    await execute(
        f"UPDATE cart_items SET {set_clause}, updated_at = NOW() WHERE id = :id",
        {"id": id, **updates}
    )

    await recalculate_cart(existing["cart_id"])

    return {"status": "success", "message": "Item updated"}


# =========================================================
# DELETE
# =========================================================
async def delete_cart_item(id: str):
    existing = await get_cart_item_by_id(id)

    if not existing:
        return None

    await execute(
        queries["cart_items"]["delete"],
        {"id": id}
    )

    await recalculate_cart(existing["cart_id"])

    return {"status": "success", "message": "Item deleted"}
import json
import uuid
import os
import shutil
from datetime import datetime
from typing import List, Dict
from fastapi import HTTPException, UploadFile

from app.core.database import execute, query, query_all
from app.utils.query_loader import load_queries

queries = load_queries()

UPLOAD_FOLDER = "media/cart_items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# FILE SAVE
# --------------------------------------------------
def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")


# --------------------------------------------------
# PRICE LOOKUP
# --------------------------------------------------
async def get_variant_price(variant_id: str, quantity: int):
    row = await query(
        """
        SELECT *
        FROM product_variant_prices
        WHERE variant_id = :variant_id
          AND is_active = 1
          AND :quantity >= min_qty
        ORDER BY min_qty DESC
        LIMIT 1
        """,
        {"variant_id": variant_id, "quantity": quantity},
    )

    if not row:
        raise HTTPException(400, "No valid price found")

    return row


# --------------------------------------------------
# RECALCULATE CART
# --------------------------------------------------
async def recalculate_cart(cart_id: str):
    result = await query(
        """
        SELECT COALESCE(SUM(total_price), 0) AS total
        FROM cart_items
        WHERE cart_id = :cart_id
        """,
        {"cart_id": cart_id},
    )

    total = result["total"] if result else 0

    await execute(
        """
        UPDATE carts
        SET total_amount = :total,
            updated_at = NOW()
        WHERE id = :cart_id
        """,
        {"total": total, "cart_id": cart_id},
    )


# --------------------------------------------------
# CREATE
# --------------------------------------------------
async def create_cart_item(payload):
    existing = await query(
        """
        SELECT *
        FROM cart_items
        WHERE cart_id = :cart_id
          AND variant_id = :variant_id
        LIMIT 1
        """,
        {"cart_id": payload.cart_id, "variant_id": payload.variant_id},
    )

    if existing:
        new_qty = existing["quantity"] + payload.quantity
        price = await get_variant_price(payload.variant_id, new_qty)

        await execute(
            """
            UPDATE cart_items
            SET quantity = :quantity,
                unit_price = :unit_price,
                total_price = :total_price,
                discount_id = :discount_id,
                updated_at = NOW()
            WHERE id = :id
            """,
            {
                "id": existing["id"],
                "quantity": new_qty,
                "unit_price": price["price"],
                "total_price": price["price"] * new_qty,
                "discount_id": price.get("discount_id"),
            },
        )

        await recalculate_cart(payload.cart_id)
        return {"message": "Item merged"}

    price = await get_variant_price(payload.variant_id, payload.quantity)
    item_id = str(uuid.uuid4())

    await execute(
        queries["cart_items"]["create"],
        {
            "id": item_id,
            "cart_id": payload.cart_id,
            "product_id": payload.product_id,
            "variant_id": payload.variant_id,
            "quantity": payload.quantity,
            "unit_price": price["price"],
            "discount_id": price.get("discount_id"),
            "total_price": price["price"] * payload.quantity,
            "selected_options": json.dumps(payload.selected_options or {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    )

    await recalculate_cart(payload.cart_id)
    return {"message": "Item added", "id": item_id}


# --------------------------------------------------
# CREATE WITH FILES
# --------------------------------------------------
async def create_cart_item_with_files(
    cart_id,
    product_id,
    variant_id,
    quantity,
    selected_options,
    front_file,
    back_file
):
    class Payload: pass

    payload = Payload()
    payload.cart_id = cart_id
    payload.product_id = product_id
    payload.variant_id = variant_id
    payload.quantity = quantity
    payload.selected_options = json.loads(selected_options)

    result = await create_cart_item(payload)

    if "id" not in result:
        return result

    item_id = result["id"]

    front_url = save_upload(front_file) if front_file else None
    back_url = save_upload(back_file) if back_file else None

    if front_url or back_url:
        await execute(
            """
            INSERT INTO cart_item_files (
                id,
                cart_item_id,
                front_side_url,
                back_side_url,
                front_original_name,
                back_original_name,
                created_at
            ) VALUES (
                :id,
                :cart_item_id,
                :front_side_url,
                :back_side_url,
                :front_original_name,
                :back_original_name,
                NOW()
            )
            """,
            {
                "id": str(uuid.uuid4()),
                "cart_item_id": item_id,
                "front_side_url": front_url,
                "back_side_url": back_url,
                "front_original_name": front_file.filename if front_file else None,
                "back_original_name": back_file.filename if back_file else None,
            },
        )

    return {"message": "Item with files added", "id": item_id}


# --------------------------------------------------
# GET
# --------------------------------------------------
async def get_cart_items_by_cart_id(cart_id: str):
    return await query_all(
        queries["cart_items"]["get_by_cart_id"],
        {"cart_id": cart_id},
    )


async def get_cart_items_by_user_id(user_id: str) -> List[Dict]:
    items = await query_all(
        queries["cart_items"]["get_by_user_id"],
        {"user_id": user_id},
    )

    for item in items:
        files = await query_all(
            queries["cart_item_files"]["get_by_cart_item_id"],
            {"cart_item_id": item["id"]},
        )
        item["files"] = files

    return items


async def get_cart_item_by_id(id: str):
    return await query(
        queries["cart_items"]["get_by_id"],
        {"id": id},
    )


# --------------------------------------------------
# UPDATE
# --------------------------------------------------
async def update_cart_item(id: str, updates: dict):
    existing = await get_cart_item_by_id(id)
    if not existing:
        return None

    if "quantity" in updates:
        price = await get_variant_price(existing["variant_id"], updates["quantity"])
        updates["unit_price"] = price["price"]
        updates["total_price"] = price["price"] * updates["quantity"]
        updates["discount_id"] = price.get("discount_id")

    if "selected_options" in updates:
        updates["selected_options"] = json.dumps(updates["selected_options"])

    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())

    await execute(
        f"""
        UPDATE cart_items
        SET {set_clause},
            updated_at = NOW()
        WHERE id = :id
        """,
        {"id": id, **updates},
    )

    await recalculate_cart(existing["cart_id"])
    return {"message": "Item updated"}


# --------------------------------------------------
# DELETE
# --------------------------------------------------
async def delete_cart_item(id: str):
    existing = await get_cart_item_by_id(id)
    if not existing:
        return None

    await execute(
        queries["cart_items"]["delete"],
        {"id": id},
    )

    await recalculate_cart(existing["cart_id"])
    return {"message": "Item deleted"}
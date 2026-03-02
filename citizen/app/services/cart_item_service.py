import json
from typing import Dict, List
import uuid
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, UploadFile
from app.utils.query_loader import load_queries
import os
import shutil

queries = load_queries()

UPLOAD_FOLDER = "media/cart_items"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"  # unique filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")  # normalize for URLs


# --------------------------------------------------
# PRICE LOOKUP (max_qty removed)
# --------------------------------------------------
async def get_variant_price(variant_id: str, quantity: int, session: AsyncSession):
    query = """
    SELECT *
    FROM product_variant_prices
    WHERE variant_id = :variant_id
      AND is_active = 1
      AND :quantity >= min_qty
    ORDER BY min_qty DESC
    LIMIT 1;
    """
    result = await session.execute(
        text(query),
        {"variant_id": variant_id, "quantity": quantity}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(400, "No valid price found")
    return dict(row._mapping)


# --------------------------------------------------
# RECALCULATE CART
# --------------------------------------------------
async def recalculate_cart(cart_id: str, session: AsyncSession):
    result = await session.execute(
        text("""
        SELECT COALESCE(SUM(total_price), 0) AS total
        FROM cart_items
        WHERE cart_id = :cart_id
        """),
        {"cart_id": cart_id}
    )
    total = result.fetchone()._mapping["total"]
    await session.execute(
        text("""
        UPDATE carts
        SET total_amount = :total,
            updated_at = NOW()
        WHERE id = :cart_id
        """),
        {"total": total, "cart_id": cart_id}
    )


# --------------------------------------------------
# CREATE (MERGE SAFE)
# --------------------------------------------------
async def create_cart_item(payload, session: AsyncSession):
    async with session.begin():

        # Check existing variant
        result = await session.execute(
            text("""
            SELECT * FROM cart_items
            WHERE cart_id = :cart_id
              AND variant_id = :variant_id
            LIMIT 1
            """),
            {
                "cart_id": payload.cart_id,
                "variant_id": payload.variant_id
            }
        )
        existing = result.fetchone()

        if existing:
            existing = dict(existing._mapping)
            new_qty = existing["quantity"] + payload.quantity

            price = await get_variant_price(payload.variant_id, new_qty, session)

            await session.execute(
                text("""
                UPDATE cart_items
                SET quantity = :quantity,
                    unit_price = :unit_price,
                    total_price = :total_price,
                    discount_id = :discount_id,
                    updated_at = NOW()
                WHERE id = :id
                """),
                {
                    "id": existing["id"],
                    "quantity": new_qty,
                    "unit_price": price["price"],
                    "total_price": price["price"] * new_qty,
                    "discount_id": price.get("discount_id")
                }
            )

            await recalculate_cart(payload.cart_id, session)
            return {"message": "Item merged"}

        # Insert new
        price = await get_variant_price(payload.variant_id, payload.quantity, session)
        item_id = str(uuid.uuid4())

        await session.execute(
            text(queries["cart_items"]["create"]),
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
                "updated_at": datetime.utcnow()
            }
        )

        await recalculate_cart(payload.cart_id, session)
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
    front_file: UploadFile | None,
    back_file: UploadFile | None,
    session
):
    class Payload: pass

    payload = Payload()
    payload.cart_id = cart_id
    payload.product_id = product_id
    payload.variant_id = variant_id
    payload.quantity = quantity
    payload.selected_options = json.loads(selected_options)

    result = await create_cart_item(payload, session)
    if "id" not in result:
        return result

    item_id = result["id"]
    front_url = save_upload(front_file) if front_file else None
    back_url = save_upload(back_file) if back_file else None

    if front_url or back_url:
        await session.execute(
            text("""
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
            """),
            {
                "id": str(uuid.uuid4()),
                "cart_item_id": item_id,
                "front_side_url": front_url,
                "back_side_url": back_url,
                "front_original_name": front_file.filename if front_file else None,
                "back_original_name": back_file.filename if back_file else None
            }
        )
        await session.commit()  # must commit

    return {"message": "Item with files added", "id": item_id}


# --------------------------------------------------
# GET
# --------------------------------------------------
async def get_cart_items_by_cart_id(cart_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["cart_items"]["get_by_cart_id"]),
        {"cart_id": cart_id}
    )
    return [dict(row._mapping) for row in result.fetchall()]

async def get_cart_items_by_user_id(user_id: str, session: AsyncSession) -> List[Dict]:
    # 1️⃣ Fetch active cart items
    result = await session.execute(
        text(queries["cart_items"]["get_by_user_id"]),
        {"user_id": user_id}
    )
    cart_items = [dict(row._mapping) for row in result.fetchall()]

    # 2️⃣ Attach files for each cart item
    for item in cart_items:
        files_result = await session.execute(
            text(queries["cart_item_files"]["get_by_cart_item_id"]),
            {"cart_item_id": item["id"]}
        )
        item["files"] = [dict(row._mapping) for row in files_result.fetchall()]

    return cart_items

# --------------------------------------------------
# UPDATE
# --------------------------------------------------
async def update_cart_item(id: str, updates: dict, session: AsyncSession):
    async with session.begin():
        result = await session.execute(
            text(queries["cart_items"]["get_by_id"]),
            {"id": id}
        )
        row = result.fetchone()
        if not row:
            return None

        existing = dict(row._mapping)

        if "quantity" in updates:
            price = await get_variant_price(existing["variant_id"], updates["quantity"], session)
            updates["unit_price"] = price["price"]
            updates["total_price"] = price["price"] * updates["quantity"]
            updates["discount_id"] = price.get("discount_id")

        if "selected_options" in updates:
            updates["selected_options"] = json.dumps(updates["selected_options"])

        set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())

        await session.execute(
            text(f"""
            UPDATE cart_items
            SET {set_clause},
                updated_at = NOW()
            WHERE id = :id
            """),
            {"id": id, **updates}
        )

        await recalculate_cart(existing["cart_id"], session)
        return {"message": "Item updated"}


# --------------------------------------------------
# DELETE
# --------------------------------------------------
async def delete_cart_item(id: str, session: AsyncSession):
    async with session.begin():
        result = await session.execute(
            text("SELECT cart_id FROM cart_items WHERE id = :id"),
            {"id": id}
        )
        row = result.fetchone()
        if not row:
            return None

        cart_id = row._mapping["cart_id"]

        await session.execute(
            text(queries["cart_items"]["delete"]),
            {"id": id}
        )

        await recalculate_cart(cart_id, session)
        return {"message": "Item deleted"}
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

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")

async def get_variant_price(variant_id: str, quantity: int):
    row = await query(
        queries["cart_items"]["variant_price_lookup"],
        {"variant_id": variant_id, "quantity": quantity},
    )
    if not row:
        raise HTTPException(400, "No valid price found")
    return row

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

async def create_cart_item(payload: Any):

    price = await get_variant_price(payload.variant_id, payload.quantity)

    existing = await query(
        queries["cart_items"]["find_existing_item"],
        {
            "cart_id": payload.cart_id,
            "variant_id": payload.variant_id
        },
    )

    if existing:
        new_qty = existing["quantity"] + payload.quantity

        await execute(
            queries["cart_items"]["merge_update"],
            {
                "id": existing["id"],
                "quantity": new_qty,
                "unit_price": price["price"],
                "total_price": price["price"] * new_qty,
                "discount_id": price.get("discount_id"),
            },
        )

        await recalculate_cart(payload.cart_id)
        return {"message": "Item merged", "id": existing["id"]}

    # CREATE NEW
    item_id = str(uuid.uuid4())

    await execute(
        queries["cart_items"]["create"],
        {
            "id": item_id,
            "cart_id": payload.cart_id,
            "product_id": payload.product_id,
            "variant_id": payload.variant_id,
            "variant_price_id": price["id"],  # ✅ correct
            "quantity": payload.quantity,
            "unit_price": price["price"],
            "total_price": price["price"] * payload.quantity,
            "discount_id": price.get("discount_id"),
            "selected_attributes": json.dumps(
                getattr(payload, 'selected_attributes', {})
            ),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    )

    await recalculate_cart(payload.cart_id)

    return {"message": "Item added", "id": item_id}

async def create_cart_item_with_files(
    cart_id, product_id, variant_id, quantity,
    selected_attributes,
    front_file, back_file
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

async def create_cart_item_with_out_files(
    cart_id, product_id, variant_id, quantity,
    product_variant_price_id, customize_qty, selected_options,
    front_file=None, back_file=None
):
    """
    Create or update a cart item with optional file uploads
    and recalculate the cart total once.
    """
    class Payload: pass

    payload = Payload()
    payload.cart_id = cart_id
    payload.product_id = product_id
    payload.variant_id = variant_id
    payload.quantity = quantity
    payload.product_variant_price_id = product_variant_price_id
    payload.customize_qty = customize_qty
    payload.selected_options = json.loads(selected_options or "{}")

    # 1️⃣ Create or update cart item
    existing_item = await query_all(
        "SELECT * FROM cart_items WHERE cart_id = %s AND variant_id = %s LIMIT 1",
        (cart_id, variant_id)
    )

    if existing_item:
        # Update existing cart item
        new_total_price = payload.quantity * payload.product_variant_price_id  # simple calculation
        await execute(
            """
            UPDATE cart_items
            SET quantity = %s,
                unit_price = %s,
                total_price = %s,
                discount_id = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (payload.quantity, payload.product_variant_price_id, new_total_price, None, existing_item["id"])
        )
        item_id = existing_item["id"]
    else:
        # Insert new cart item
        item_id = str(uuid.uuid4())
        await execute(
            """
            INSERT INTO cart_items (id, cart_id, product_id, variant_id, quantity,
                unit_price, total_price, customize_qty, selected_options, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
            """,
            (
                item_id,
                cart_id,
                product_id,
                variant_id,
                quantity,
                product_variant_price_id,
                quantity * product_variant_price_id,
                customize_qty,
                json.dumps(payload.selected_options)
            )
        )

    # 2️⃣ Handle file uploads
    if front_file and front_file.file:
        front_url = save_upload(front_file)
        await execute(
            """
            INSERT INTO cart_item_files (id, cart_item_id, front_side_url, front_original_name)
            VALUES (%s,%s,%s,%s)
            """,
            (str(uuid.uuid4()), item_id, front_url, front_file.filename)
        )
    if back_file and back_file.file:
        back_url = save_upload(back_file)
        await execute(
            """
            INSERT INTO cart_item_files (id, cart_item_id, back_side_url, back_original_name)
            VALUES (%s,%s,%s,%s)
            """,
            (str(uuid.uuid4()), item_id, back_url, back_file.filename)
        )

    # 3️⃣ Recalculate cart total once
    total = await query_all(
        "SELECT COALESCE(SUM(total_price),0) AS total FROM cart_items WHERE cart_id = %s",
        (cart_id,)
    )
    await execute(
        "UPDATE carts SET total_amount = %s, updated_at = %s WHERE id = %s",
        (total["total"], datetime.utcnow(), cart_id)
    )

    # 4️⃣ Return the cart item info
    result = await query_all("SELECT * FROM cart_items WHERE id = %s", (item_id,))
    return result
# Keep all other functions unchanged (get, update, delete)...
async def get_cart_items_by_cart_id(cart_id: str):
    return await query_all(queries["cart_items"]["get_by_cart_id"], {"cart_id": cart_id})

async def get_cart_items_by_user_id(user_id: str) -> List[Dict]:
    items = await query_all(queries["cart_items"]["get_by_user_id"], {"user_id": user_id})
    for item in items:
        files = await query_all(
            queries["cart_items"]["get_files_by_cart_item_id"],
            {"cart_item_id": item["id"]}
        )
        item["files"] = files
    return items

async def get_cart_item_by_id(id: str):
    return await query(queries["cart_items"]["get_by_id"], {"id": id})

async def update_cart_item(id: str, updates: dict):
    existing = await get_cart_item_by_id(id)
    if not existing: return None
    if "quantity" in updates:
        price = await get_variant_price(existing["variant_id"], updates["quantity"])
        updates["unit_price"] = price["price"]
        updates["total_price"] = price["price"] * updates["quantity"]
        updates["discount_id"] = price.get("discount_id")
    if "selected_options" in updates:
        updates["selected_options"] = json.dumps(updates["selected_options"])
    set_clause = ", ".join(f"{k} = :{k}" for k in updates.keys())
    await execute(f"UPDATE cart_items SET {set_clause}, updated_at = NOW() WHERE id = :id", {"id": id, **updates})
    await recalculate_cart(existing["cart_id"])
    return {"message": "Item updated"}

async def delete_cart_item(id: str):
    existing = await get_cart_item_by_id(id)
    if not existing: return None
    await execute(queries["cart_items"]["delete"], {"id": id})
    await recalculate_cart(existing["cart_id"])
    return {"message": "Item deleted"}

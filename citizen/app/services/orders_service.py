from datetime import datetime
import os
import shutil
from typing import List
from uuid import uuid4
import uuid

from fastapi import UploadFile
from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.order_domain import Order
from app.utils.query_loader import load_queries

queries = load_queries()

# CREATE
async def create_order(order: Order, session: AsyncSession):
    await session.execute(
        text(queries["order"]["create"]),
        order.to_dict()
    )
    await session.commit()
    result = await session.execute(
        text(queries["order"]["get_by_id"]),
        {"id": order.id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None

# GET ALL
async def get_all_orders(user_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["order"]["get_all"]),
        {"user_id": user_id}
    )
    return [dict(row._mapping) for row in result.fetchall()]

# GET BY ID
async def get_order_by_id(id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["order"]["get_by_id"]),
        {"id": id}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None

# UPDATE
async def update_order(id: str, updates: dict, session: AsyncSession):
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    await session.execute(
        text(queries["order"]["update"].format(set_clause=set_clause)),
        {"id": id, **updates}
    )
    await session.commit()
    return await get_order_by_id(id, session)

# DELETE
async def delete_order(id: str, session: AsyncSession):
    existing = await get_order_by_id(id, session)
    if not existing:
        return None
    await session.execute(text(queries["order"]["delete"]), {"id": id})
    await session.commit()
    return {"id": id}


UPLOAD_FOLDER = "media/orderfiles"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"  # unique filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")

# -------------------------------
# Checkout Function
# -------------------------------
async def checkout(
    user_id: str,
    cart_id: str,
    cart_item_ids: List[str],
    address_id: str,
    session: AsyncSession
):
    if not cart_item_ids:
        raise Exception("No cart items provided")

    async with session.begin():
        now = datetime.utcnow()

        # 1️⃣ Lock selected cart items
        result = await session.execute(
            text("""
                SELECT *
                FROM cart_items
                WHERE cart_id = :cart_id
                AND id IN :cart_item_ids
                FOR UPDATE
            """).bindparams(bindparam("cart_item_ids", expanding=True)),
            {"cart_id": cart_id, "cart_item_ids": cart_item_ids}
        )
        rows = result.fetchall()
        if not rows:
            raise Exception("Cart items not found")
        if len(rows) != len(cart_item_ids):
            raise Exception("Some cart items not found")

        cart_items = [dict(row._mapping) for row in rows]

        # 2️⃣ Calculate order total
        order_total = sum(item["total_price"] for item in cart_items)

        # 3️⃣ Create Order
        order_id = str(uuid.uuid4())
        await session.execute(
            text("""
                INSERT INTO orders (
                    id,
                    user_id,
                    cart_id,
                    address_id,
                    status,
                    total_amount,
                    created_at,
                    updated_at
                ) VALUES (
                    :id, :user_id, :cart_id, :address_id, :status,
                    :total_amount, :created_at, :updated_at
                )
            """),
            {
                "id": order_id,
                "user_id": user_id,
                "cart_id": cart_id,
                "address_id": address_id,
                "status": "pending",
                "total_amount": order_total,
                "created_at": now,
                "updated_at": now
            }
        )

        # 4️⃣ Create Order Items & Copy Files
        for item in cart_items:
            # Insert order_item
            result_insert = await session.execute(
                text("""
                    INSERT INTO order_items (
                        order_id,
                        cart_item_id,
                        product_id,
                        variant_id,
                        quantity,
                        price,
                        total,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :order_id, :cart_item_id, :product_id, :variant_id,
                        :quantity, :price, :total, :created_at, :updated_at
                    )
                """),
                {
                    "order_id": order_id,
                    "cart_item_id": item["id"],
                    "product_id": item["product_id"],
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],
                    "price": item["unit_price"],
                    "total": item["total_price"],
                    "created_at": now,
                    "updated_at": now
                }
            )

            # get order_item id (auto-increment)
            order_item_id = result_insert.lastrowid

            # Fetch cart item files
            files_result = await session.execute(
                text("SELECT * FROM cart_item_files WHERE cart_item_id = :cart_item_id"),
                {"cart_item_id": item["id"]}
            )
            cart_files = [dict(row._mapping) for row in files_result.fetchall()]

            # Copy files to order_item_files
            for f in cart_files:
                new_front_url = None
                new_back_url = None

                if f["front_side_url"]:
                    filename = os.path.basename(f["front_side_url"])
                    new_front_path = os.path.join(UPLOAD_FOLDER, filename)
                    shutil.copy(f["front_side_url"], new_front_path)
                    new_front_url = new_front_path.replace("\\", "/")

                if f["back_side_url"]:
                    filename = os.path.basename(f["back_side_url"])
                    new_back_path = os.path.join(UPLOAD_FOLDER, filename)
                    shutil.copy(f["back_side_url"], new_back_path)
                    new_back_url = new_back_path.replace("\\", "/")

                await session.execute(
                    text("""
                        INSERT INTO order_item_files (
                            id,
                            order_item_id,
                            front_side_url,
                            back_side_url,
                            front_original_name,
                            back_original_name,
                            created_at
                        )
                        VALUES (
                            :id, :order_item_id, :front_side_url,
                            :back_side_url, :front_original_name,
                            :back_original_name, :created_at
                        )
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "order_item_id": order_item_id,
                        "front_side_url": new_front_url,
                        "back_side_url": new_back_url,
                        "front_original_name": f["front_original_name"],
                        "back_original_name": f["back_original_name"],
                        "created_at": now
                    }
                )

        # 5️⃣ Soft delete purchased cart items
        await session.execute(
            text("""
                UPDATE cart_items
                SET status = 'purchased', updated_at = :updated_at
                WHERE id IN :cart_item_ids
            """).bindparams(bindparam("cart_item_ids", expanding=True)),
            {"cart_item_ids": cart_item_ids, "updated_at": now}
        )

        # 6️⃣ Recalculate remaining cart total
        result = await session.execute(
            text("""
                SELECT COALESCE(SUM(total_price), 0) AS total
                FROM cart_items
                WHERE cart_id = :cart_id
                AND status = 'active'
            """),
            {"cart_id": cart_id}
        )
        new_total = result.fetchone()._mapping["total"]

        await session.execute(
            text("""
                UPDATE carts
                SET total_amount = :total,
                    updated_at = :updated_at
                WHERE id = :cart_id
            """),
            {"total": new_total, "updated_at": now, "cart_id": cart_id}
        )

    return {
        "status": "success",
        "order_id": order_id,
        "total_amount": order_total
    }
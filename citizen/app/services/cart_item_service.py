import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.domain.cart_item_domain import CartItem
from app.utils.query_loader import load_queries

queries = load_queries()

# ============================================================
# PRICE LOOKUP (Robust Slab Logic)
# ============================================================
async def get_variant_price(
    variant_id: str,
    quantity: int,
    session: AsyncSession
):
    if quantity <= 0:
        raise HTTPException(400, "Quantity must be greater than zero")

    query = """
    SELECT *
    FROM product_variant_prices
    WHERE variant_id = :variant_id
      AND is_active = 1
      AND :quantity >= min_qty
      AND (
            max_qty IS NULL
            OR :quantity <= max_qty
          )
    ORDER BY min_qty DESC
    LIMIT 1;
    """

    result = await session.execute(
        text(query),
        {"variant_id": variant_id, "quantity": quantity}
    )

    row = result.fetchone()

    if not row:
        raise HTTPException(
            400,
            f"No active price found for quantity {quantity}"
        )

    return dict(row._mapping)


# ============================================================
# RECALCULATE CART TOTAL
# ============================================================
async def recalculate_cart_totals(cart_id: str, session: AsyncSession):
    total_query = """
    SELECT COALESCE(SUM(total_price), 0) AS total_amount
    FROM cart_items
    WHERE cart_id = :cart_id;
    """

    result = await session.execute(text(total_query), {"cart_id": cart_id})
    total_amount = result.fetchone()._mapping["total_amount"]

    await session.execute(
        text("""
            UPDATE carts
            SET total_amount = :total_amount,
                updated_at = NOW()
            WHERE id = :cart_id
        """),
        {"total_amount": total_amount, "cart_id": cart_id}
    )


# ============================================================
# CREATE / ADD TO CART
# ============================================================
async def create_cart_item(item: CartItem, session: AsyncSession):

    async with session.begin():

        # Validate cart
        cart_check = await session.execute(
            text("SELECT id FROM carts WHERE id = :cart_id"),
            {"cart_id": item.cart_id}
        )
        if not cart_check.fetchone():
            raise HTTPException(404, "Cart not found")

        # Check existing item
        existing_query = """
        SELECT *
        FROM cart_items
        WHERE cart_id = :cart_id
          AND variant_id = :variant_id
        LIMIT 1;
        """

        result = await session.execute(
            text(existing_query),
            {"cart_id": item.cart_id, "variant_id": item.variant_id}
        )

        existing = result.fetchone()

        # ----------------------------------------------------
        # MERGE IF EXISTS
        # ----------------------------------------------------
        if existing:
            existing = dict(existing._mapping)
            new_quantity = existing["quantity"] + item.quantity

            price = await get_variant_price(
                item.variant_id,
                new_quantity,
                session
            )

            unit_price = price["price"]
            total_price = unit_price * new_quantity

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
                    "quantity": new_quantity,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "discount_id": price.get("discount_id")
                }
            )

            await recalculate_cart_totals(item.cart_id, session)

            return {"message": "Cart item merged successfully"}

        # ----------------------------------------------------
        # INSERT NEW
        # ----------------------------------------------------
        price = await get_variant_price(
            item.variant_id,
            item.quantity,
            session
        )

        item.unit_price = price["price"]
        item.discount_id = price.get("discount_id")
        item.total_price = item.unit_price * item.quantity
        item.selected_options = json.dumps(item.selected_options or {})

        insert_query = """
        INSERT INTO cart_items (
            id,
            cart_id,
            product_id,
            variant_id,
            quantity,
            unit_price,
            total_price,
            discount_id,
            selected_options,
            created_at,
            updated_at
        ) VALUES (
            :id,
            :cart_id,
            :product_id,
            :variant_id,
            :quantity,
            :unit_price,
            :total_price,
            :discount_id,
            :selected_options,
            NOW(),
            NOW()
        );
        """

        await session.execute(text(insert_query), item.to_dict())

        await recalculate_cart_totals(item.cart_id, session)

        return {"message": "Cart item added successfully"}


# ============================================================
# GET CART ITEMS
# ============================================================
async def get_cart_items_by_cart_id(
    cart_id: str,
    session: AsyncSession
):
    query = """
    SELECT *
    FROM cart_items
    WHERE cart_id = :cart_id
    ORDER BY created_at DESC;
    """

    result = await session.execute(
        text(query),
        {"cart_id": cart_id}
    )

    rows = result.fetchall()

    items = []
    for row in rows:
        item = dict(row._mapping)
        if item.get("selected_options"):
            item["selected_options"] = json.loads(item["selected_options"])
        items.append(item)

    return items


# ============================================================
# UPDATE CART ITEM
# ============================================================
async def update_cart_item(
    id: str,
    updates: dict,
    session: AsyncSession
):

    async with session.begin():

        result = await session.execute(
            text("SELECT * FROM cart_items WHERE id = :id"),
            {"id": id}
        )

        row = result.fetchone()
        if not row:
            return None

        existing = dict(row._mapping)
        cart_id = existing["cart_id"]

        # If quantity changes → recalc price
        if "quantity" in updates:
            if updates["quantity"] <= 0:
                raise HTTPException(400, "Quantity must be greater than zero")

            price = await get_variant_price(
                existing["variant_id"],
                updates["quantity"],
                session
            )

            updates["unit_price"] = price["price"]
            updates["total_price"] = (
                updates["unit_price"] * updates["quantity"]
            )
            updates["discount_id"] = price.get("discount_id")

        if "selected_options" in updates:
            updates["selected_options"] = json.dumps(
                updates["selected_options"] or {}
            )

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

        await recalculate_cart_totals(cart_id, session)

        result = await session.execute(
            text("SELECT * FROM cart_items WHERE id = :id"),
            {"id": id}
        )

        updated = dict(result.fetchone()._mapping)
        updated["selected_options"] = json.loads(
            updated.get("selected_options") or "{}"
        )

        return updated


# ============================================================
# DELETE CART ITEM
# ============================================================
async def delete_cart_item(
    id: str,
    session: AsyncSession
):

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
            text("DELETE FROM cart_items WHERE id = :id"),
            {"id": id}
        )

        await recalculate_cart_totals(cart_id, session)

        return {"message": "Cart item deleted successfully"}
    

async def get_cart_items_by_user_id(
    user_id: str,
    session: AsyncSession
):

    result = await session.execute(
        text(queries["cart_items"]["get_by_user_id"]),
        {"user_id": user_id}
    )

    rows = result.fetchall()

    items = [dict(row._mapping) for row in rows]

    return items
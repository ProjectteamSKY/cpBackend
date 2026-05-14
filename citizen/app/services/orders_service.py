
# app/services/orders_service.py
from datetime import datetime
import os
import shutil
import uuid
from typing import List

from app.core.database import execute, query, query_all
from app.utils.query_loader import load_queries

queries = load_queries()

# Folder to store uploaded files for orders
UPLOAD_FOLDER = "media/orderfiles"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file) -> str:
    """Save uploaded file and return path"""
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")

async def checkout(
    user_id: str,
    cart_id: str,
    cart_items: list,
    address_id: str,
    payment_method: str = "COD",
    delivery_type: str = "normal",
    courier_id: str = None,
    courier_name: str = None,
    delivery_charge: float = 0
):

    if not cart_items:
        raise Exception("No cart items provided")

    now = datetime.utcnow()

    # ---------------------------------------------------------
    # VALIDATE CART
    # ---------------------------------------------------------
    cart_check = await query("""
        SELECT status FROM carts WHERE id = :cart_id
    """, {"cart_id": cart_id})

    if not cart_check:
        raise Exception("Cart not found")

    if cart_check["status"] != "active":
        raise Exception("Cart already checked out or inactive")

    order_id = str(uuid.uuid4())
    order_number = await generate_order_number()

    # ---------------------------------------------------------
    # LOCK ACTIVE CART ITEMS
    # ---------------------------------------------------------
    cart_item_ids = [item["cart_item_id"] for item in cart_items]

    placeholders = ", ".join(f":id{i}" for i in range(len(cart_item_ids)))
    params = {"cart_id": cart_id}
    params.update({f"id{i}": cid for i, cid in enumerate(cart_item_ids)})

    rows = await query_all(f"""
        SELECT *
        FROM cart_items
        WHERE cart_id = :cart_id
        AND id IN ({placeholders})
        AND status = 'active'
        FOR UPDATE
    """, params)

    if len(rows) != len(cart_item_ids):
        raise Exception("Some cart items not found or already processed")

    order_total = sum(float(r["total_price"]) for r in rows)

    # ---------------------------------------------------------
    # PAYMENT STATUS LOGIC
    # ---------------------------------------------------------
    payment_status = "paid" if payment_method == "PREPAID" else "pending"

    # ---------------------------------------------------------
    # CREATE ORDER
    # ---------------------------------------------------------
    await execute("""
        INSERT INTO orders (
            id, order_number, user_id, cart_id, address_id,
            delivery_charge, courier_id, courier_name,
            delivery_type, payment_method, payment_status,
            status, total_amount, created_at, updated_at
        )
        VALUES (
            :id, :order_number, :user_id, :cart_id, :address_id,
            :delivery_charge, :courier_id, :courier_name,
            :delivery_type, :payment_method, :payment_status,
            'pending', :total_amount, :created_at, :updated_at
        )
    """, {
        "id": order_id,
        "order_number": order_number,
        "user_id": user_id,
        "cart_id": cart_id,
        "address_id": address_id,
        "delivery_charge": delivery_charge,
        "courier_id": courier_id,
        "courier_name": courier_name,
        "delivery_type": delivery_type,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "total_amount": order_total,
        "created_at": now,
        "updated_at": now
    })

    # ---------------------------------------------------------
    # CREATE ORDER ITEMS + COPY FILES
    # ---------------------------------------------------------
    for item in rows:
        order_item_id = str(uuid.uuid4())

        await execute("""
            INSERT INTO order_items (
                id, order_id, product_id, variant_id,
                variant_price_id, customize_qty,
                quantity, unit_price, total_price,
                selected_attributes, discount_id,
                status, created_at, updated_at
            )
            VALUES (
                :id, :order_id, :product_id, :variant_id,
                :variant_price_id, :customize_qty,
                :quantity, :unit_price, :total_price,
                :selected_attributes, :discount_id,
                'pending', :created_at, :updated_at
            )
        """, {
            "id": order_item_id,
            "order_id": order_id,
            "product_id": item["product_id"],
            "variant_id": item["variant_id"],
            "variant_price_id": item["variant_price_id"],
            "customize_qty": item.get("customize_qty"),
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "total_price": item["total_price"],
            "selected_attributes": item.get("selected_attributes"),
            "discount_id": item.get("discount_id"),
            "created_at": now,
            "updated_at": now
        })

        # ---------------------------------------------------------
        # COPY CART ITEM FILES → ORDER ITEM FILES
        # ---------------------------------------------------------
        files = await query_all("""
            SELECT *
            FROM cart_item_files
            WHERE cart_item_id = :cart_item_id
        """, {"cart_item_id": item["id"]})

        if files:
            for f in files:

                # skip empty rows
                if not f.get("front_side_url") and not f.get("back_side_url"):
                    continue

                await execute("""
                    INSERT INTO order_item_files (
                        id, order_item_id,
                        front_side_url, back_side_url,
                        front_original_name, back_original_name
                    )
                    VALUES (
                        :id, :order_item_id,
                        :front_side_url, :back_side_url,
                        :front_original_name, :back_original_name
                    )
                """, {
                    "id": str(uuid.uuid4()),
                    "order_item_id": order_item_id,
                    "front_side_url": f.get("front_side_url"),
                    "back_side_url": f.get("back_side_url"),
                    "front_original_name": f.get("front_original_name"),
                    "back_original_name": f.get("back_original_name"),
                })

    # ---------------------------------------------------------
    # UPDATE CART ITEMS → ORDERED
    # ---------------------------------------------------------
    await execute("""
        UPDATE cart_items
        SET status = 'ordered',
            updated_at = :now
        WHERE cart_id = :cart_id
    """, {
        "cart_id": cart_id,
        "now": now
    })

    # ---------------------------------------------------------
    # UPDATE CART → ORDERED
    # ---------------------------------------------------------
    await execute("""
        UPDATE carts
        SET status = 'ordered',
            updated_at = :now
        WHERE id = :cart_id
    """, {
        "cart_id": cart_id,
        "now": now
    })

    # ---------------------------------------------------------
    # AUTO CONFIRM PREPAID ORDERS
    # ---------------------------------------------------------
    if payment_method == "PREPAID":
        await execute("""
            UPDATE orders
            SET status = 'pending'
            WHERE id = :order_id
        """, {"order_id": order_id})

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------
    return {
        "status": "success",
        "order_id": order_id,
        "order_number": order_number,
        "total_amount": order_total,
        "payment_status": payment_status
    }
# Rest of functions unchanged...
ORDER_STATUS_FLOW = {
    "pending": ["process"],
    "process": ["printing"],
    "printing": ["packed"],
    "packed": ["shipment"],
    "shipment": ["delivery"],
    "delivery": [],
}

async def get_all_orders_tracking():
    return await query_all("""
        SELECT 
            o.*,

            -- USER
            u.full_name,
            u.email,
            u.contact AS user_phone,

            -- ADDRESS
            ua.first_name,
            ua.last_name,
            ua.address AS address_line,
            ua.landmark,
            ua.city,
            ua.state,
            ua.country,
            ua.postal_code,
            ua.phone AS address_phone,

            -- SHIPMENT
            s.awb_code,
            s.courier_name AS shipment_courier,
            s.freight_charges,
            s.tracking_url,
            s.current_status,
            s.pickup_status,
            s.delivered_at

        FROM orders o

        LEFT JOIN users u 
            ON o.user_id = u.id

        LEFT JOIN user_addresses ua 
            ON o.address_id = ua.id

        LEFT JOIN shipments s 
            ON o.id = s.order_id

        ORDER BY o.created_at DESC
    """, {})

async def get_order_items(order_id):
    return await query_all("""
        SELECT 
            oi.*,
            p.name AS product_name,

            oif.front_side_url,
            oif.back_side_url,
            oif.front_original_name,
            oif.back_original_name

        FROM order_items oi

        LEFT JOIN products p 
            ON oi.product_id = p.id

        LEFT JOIN order_item_files oif 
            ON oi.id = oif.order_item_id

        WHERE oi.order_id = :order_id
        ORDER BY oi.created_at
    """, {"order_id": order_id})


async def get_order_by_id(order_id: str):
    return await query("SELECT * FROM orders WHERE id = :id", {"id": order_id})

async def update_order(order_id: str, updates: dict):
    if not updates:
        return await get_order_by_id(order_id)
    set_clause = ", ".join(f"{key} = :{key}" for key in updates.keys())
    params = {"id": order_id, **updates}
    await execute(
        f"UPDATE orders SET {set_clause}, updated_at = NOW() WHERE id = :id",
        params,
    )
    return await get_order_by_id(order_id)

async def delete_order(order_id: str):
    existing = await get_order_by_id(order_id)
    if not existing:
        return None
    await execute("DELETE FROM orders WHERE id = :id", {"id": order_id})
    return {"id": order_id}

async def get_order_items(order_id):
    return await query_all("""
        SELECT 
            oi.*,
            p.name AS product_name,

            oif.id AS file_id,
            oif.front_side_url,
            oif.back_side_url,
            oif.front_original_name,
            oif.back_original_name

        FROM order_items oi

        LEFT JOIN products p 
            ON oi.product_id = p.id

        LEFT JOIN order_item_files oif 
            ON oi.id = oif.order_item_id

        WHERE oi.order_id = :order_id
        ORDER BY oi.id
    """, {"order_id": order_id})

async def update_order_status(order_id: str, new_status: str):
    order = await get_order_by_id(order_id)
    if not order:
        raise Exception("Order not found")
    current_status = order["status"]
    allowed = ORDER_STATUS_FLOW.get(current_status, [])
    if new_status not in allowed:
        raise Exception(f"Invalid status transition: {current_status} → {new_status}")
    await execute(
        "UPDATE orders SET status = :status, updated_at = NOW() WHERE id = :id",
        {"status": new_status, "id": order_id},
    )
    return {
        "order_id": order_id,
        "old_status": current_status,
        "new_status": new_status,
    }

async def get_user_orders(user_id: str):
    """Get all orders with items + files (optimized)"""

    # 1️⃣ Get orders
    orders = await query_all(
        """
        SELECT *
        FROM orders
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        """,
        {"user_id": user_id}
    )

    if not orders:
        return []

    order_ids = [o["id"] for o in orders]

    # 2️⃣ Get all order items in ONE query
    items = await query_all(
        """
        SELECT 
            oi.id,
            oi.order_id,
            oi.product_id,
            oi.variant_id,
            oi.variant_price_id,
            oi.customize_qty,
            oi.quantity,
            oi.unit_price,
            oi.total_price,
            oi.selected_attributes,
            oi.discount_id,
            p.name AS product_name
        FROM order_items oi
        LEFT JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id IN :order_ids
        """,
        {"order_ids": tuple(order_ids)}
    )

    # 3️⃣ Get all files in ONE query
    item_ids = [i["id"] for i in items]

    files = []
    if item_ids:
        files = await query_all(
            """
            SELECT *
            FROM order_item_files
            WHERE order_item_id IN :item_ids
            """,
            {"item_ids": tuple(item_ids)}
        )

    # 4️⃣ Map files to items
    file_map = {}
    for f in files:
        file_map.setdefault(f["order_item_id"], []).append(f)

    # attach files to items
    for item in items:
        item["files"] = file_map.get(item["id"], [])

    # 5️⃣ Group items under orders
    order_map = {o["id"]: o for o in orders}
    for o in orders:
        o["products"] = []

    for item in items:
        order_map[item["order_id"]]["products"].append(item)

    return orders


async def get_total_orders():

    result = await query(
        queries["order"]["get_total_orders"],
        {},
    )
    print("total orders@@@@@@@@@@@@@@@@@@@@@@@@@@@@",result)
    if not result:
        return {"total_orders": 0}

    return {
        "total_orders": result["total_orders"]
    }

async def get_total_orders_by_user(user_id: str):

    result = await query(
        queries["order"]["get_total_orders_by_user"],
        {"user_id": user_id},
    )

    if not result:
        return {"total_orders": 0}

    return {
        "user_id": user_id,
        "total_orders": result["total_orders"],
    }

async def get_orders_summary():

    result = await query(
        queries["order"]["get_orders_summary"],
        {},
    )

    if not result:
        return {}

    return {
        "total_orders": result["total_orders"],
        "pending_orders": result["pending_orders"],
        "process_orders": result["process_orders"],
        "printing_orders": result["printing_orders"],
        "packed_orders": result["packed_orders"],
        "shipment_orders": result["shipment_orders"],
        "delivery_orders": result["delivery_orders"],
    }


async def get_monthly_revenue():

    rows = await query_all(
        queries["order"]["get_monthly_revenue"],
        {},
    )

    return rows

async def get_top_products():

    rows = await query_all(
        queries["order"]["get_top_products"],
        {},
    )

    return rows

async def get_recent_orders():

    rows = await query_all(
        queries["order"]["get_recent_orders"],
        {},
    )

    return rows

async def generate_order_number():

    row = await query(
        queries["order"]["get_last_order_number"],
        {}
    )

    year = datetime.utcnow().year

    if not row or not row["order_number"]:
        return f"ORD-{year}-0001"

    last = row["order_number"]

    number = int(last.split("-")[-1]) + 1

    return f"ORD-{year}-{number:04d}"

CANCEL_BLOCKED_STATUSES = [
    "printing",
    "packed",
    "shipment",
    "delivery"
]

async def update_order_status(order_id: str, new_status: str):
    order = await get_order_by_id(order_id)

    if not order:
        raise Exception("Order not found")

    current_status = order["status"]

    # ❌ Prevent updates if cancelled
    if current_status == "cancelled":
        raise Exception("Cancelled orders cannot be updated")

    allowed = ORDER_STATUS_FLOW.get(current_status, [])

    if new_status not in allowed:
        raise Exception(f"Invalid status transition: {current_status} → {new_status}")

    await execute(
        "UPDATE orders SET status = :status, updated_at = NOW() WHERE id = :id",
        {"status": new_status, "id": order_id},
    )

    return {
        "order_id": order_id,
        "old_status": current_status,
        "new_status": new_status,
    }


async def cancel_order(order_id: str):
    order = await get_order_by_id(order_id)

    if not order:
        raise Exception("Order not found")

    current_status = order["status"]

    # ❌ Block cancel after printing starts
    if current_status in CANCEL_BLOCKED_STATUSES:
        raise Exception(
            f"Cannot cancel order after printing started (current: {current_status})"
        )

    # ✔ Already cancelled check
    if current_status == "cancelled":
        return {
            "order_id": order_id,
            "status": "already_cancelled"
        }

    await execute(
        """
        UPDATE orders
        SET status = 'cancelled',
            updated_at = NOW()
        WHERE id = :id
        """,
        {"id": order_id}
    )

    return {
        "order_id": order_id,
        "old_status": current_status,
        "new_status": "cancelled"
    }

# =========================================================
# SALES SUMMARY
# =========================================================
async def get_sales_summary():

    result = await query("""
        SELECT
            COUNT(DISTINCT o.id) AS total_orders,

            COALESCE(SUM(oi.total_price), 0) AS total_sales,

            COALESCE(AVG(o.total_amount), 0) AS average_order_value,

            COALESCE(SUM(o.delivery_charge), 0) AS total_delivery_charge,

            -- TOTAL UNITS SOLD
            COALESCE(SUM(oi.quantity), 0) AS total_units_sold,

            -- TOTAL UNIQUE PRODUCTS
            COUNT(DISTINCT oi.product_id) AS total_unique_products

        FROM orders o

        LEFT JOIN order_items oi
            ON o.id = oi.order_id

        WHERE o.status != 'cancelled'
    """, {})

    return {
        "total_orders": int(result["total_orders"] or 0),

        "total_sales": float(result["total_sales"] or 0),

        "average_order_value": float(result["average_order_value"] or 0),

        "total_delivery_charge": float(result["total_delivery_charge"] or 0),

        "total_units_sold": int(result["total_units_sold"] or 0),

        "total_unique_products": int(result["total_unique_products"] or 0),
    }


# =========================================================
# SALES REPORT WITH FULL DETAILS
# =========================================================
async def get_sales_report(
    start_date: str = None,
    end_date: str = None,
    status: str = None
):

    where_clause = "WHERE o.status != 'cancelled'"
    params = {}

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------
    if start_date:
        where_clause += " AND DATE(o.created_at) >= :start_date"
        params["start_date"] = start_date

    if end_date:
        where_clause += " AND DATE(o.created_at) <= :end_date"
        params["end_date"] = end_date

    if status:
        where_clause += " AND o.status = :status"
        params["status"] = status

    # -----------------------------------------------------
    # FETCH SALES REPORT
    # -----------------------------------------------------
    rows = await query_all(f"""
        SELECT

            -- ORDER
            o.id AS order_id,
            o.order_number,
            o.status,
            o.payment_method,
            o.payment_status,
            o.delivery_type,
            o.delivery_charge,
            o.total_amount,

            -- FIXED DATE FORMAT
            DATE_FORMAT(
                o.created_at,
                '%Y-%m-%d %H:%i:%s'
            ) AS created_at,

            -- CUSTOMER
            u.full_name AS customer_name,
            u.email,

            -- PHONE
            ua.phone AS phone,

            -- PRODUCT
            p.id AS product_id,
            p.name AS product_name,

            -- ORDER ITEM
            oi.quantity AS qty,
            oi.unit_price,
            oi.total_price,

            -- SHIPMENT
            s.awb_code,
            s.courier_name,
            s.current_status AS shipment_status,
            s.tracking_url

        FROM orders o

        LEFT JOIN users u
            ON o.user_id = u.id

        LEFT JOIN user_addresses ua
            ON o.address_id = ua.id

        LEFT JOIN order_items oi
            ON o.id = oi.order_id

        LEFT JOIN products p
            ON oi.product_id = p.id

        LEFT JOIN shipments s
            ON o.id = s.order_id

        {where_clause}

        ORDER BY o.created_at DESC

    """, params)

    # -----------------------------------------------------
    # GROUP ORDERS
    # -----------------------------------------------------
    orders_map = {}

    for row in rows:

        order_id = row.get("order_id")

        # -------------------------------------------------
        # CREATE ORDER
        # -------------------------------------------------
        if order_id not in orders_map:

            delivery_charge = float(
                row.get("delivery_charge") or 0
            )

            orders_map[order_id] = {

                # ORDER
                "order_id": order_id,

                "order_number": row.get("order_number"),

                "status": row.get("status"),

                "payment_method": row.get("payment_method"),

                "payment_status": row.get("payment_status"),

                "delivery_type": row.get("delivery_type"),

                # DATE
                "date": row.get("created_at"),

                # CUSTOMER
                "customer": {
                    "name": row.get("customer_name"),
                    "email": row.get("email"),
                    "phone": row.get("phone")
                },

                # SHIPMENT
                "shipment": {
                    "awb_code": row.get("awb_code"),
                    "courier_name": row.get("courier_name"),
                    "shipment_status": row.get("shipment_status"),
                    "tracking_url": row.get("tracking_url")
                } if row.get("awb_code") else None,

                # PRODUCTS
                "products": [],

                # TOTALS
                "product_total": 0.0,

                "delivery_charge": delivery_charge,

                "final_amount": 0.0,

                # TOTAL QTY
                "total_qty": 0
            }

        # -------------------------------------------------
        # PRODUCT DETAILS
        # -------------------------------------------------
        if row.get("product_id"):

            qty = int(row.get("qty") or 0)

            unit_price = float(
                row.get("unit_price") or 0
            )

            total_price = float(
                row.get("total_price") or 0
            )

            product_data = {

                "product_id": row.get("product_id"),

                "product_name": row.get("product_name"),

                "qty": qty,

                "unit_price": unit_price,

                "total_price": total_price
            }

            # ADD PRODUCT
            orders_map[order_id]["products"].append(
                product_data
            )

            # PRODUCT TOTAL
            orders_map[order_id]["product_total"] += total_price

            # TOTAL QTY
            orders_map[order_id]["total_qty"] += qty

    # -----------------------------------------------------
    # FINAL CALCULATIONS
    # -----------------------------------------------------
    total_sales = 0.0

    total_qty = 0

    for order in orders_map.values():

        order["product_total"] = round(
            order["product_total"],
            2
        )

        # FINAL AMOUNT
        order["final_amount"] = round(
            order["product_total"] +
            order["delivery_charge"],
            2
        )

        total_sales += order["final_amount"]

        total_qty += order["total_qty"]

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------
    return {

        "total_orders": len(orders_map),

        "total_sales": round(total_sales, 2),

        "total_qty": total_qty,

        "orders": list(orders_map.values())
    }
# =========================================================
# SALES BY STATUS
# =========================================================
async def get_sales_by_status():

    rows = await query_all("""
        SELECT

            o.status,

            COUNT(DISTINCT o.id) AS total_orders,

            COALESCE(SUM(o.total_amount), 0) AS total_sales,

            -- TOTAL UNITS SOLD
            COALESCE(SUM(oi.quantity), 0) AS total_units_sold,

            -- TOTAL UNIQUE PRODUCTS
            COUNT(DISTINCT oi.product_id) AS total_unique_products,

            -- PRODUCT NAMES
            GROUP_CONCAT(
                DISTINCT p.name
                ORDER BY p.name ASC
            ) AS product_names

        FROM orders o

        LEFT JOIN order_items oi
            ON o.id = oi.order_id

        LEFT JOIN products p
            ON oi.product_id = p.id

        WHERE o.status = 'shipment'

        GROUP BY o.status

        ORDER BY total_orders DESC
    """, {})

    return rows


# =========================================================
# DAILY SALES REPORT
# =========================================================
async def get_daily_sales():

    rows = await query_all("""
        SELECT

            DATE(o.created_at) AS sale_date,

            COUNT(DISTINCT o.id) AS total_orders,

            COALESCE(SUM(o.total_amount), 0) AS total_sales,

            -- TOTAL UNITS SOLD
            COALESCE(SUM(oi.quantity), 0) AS total_units_sold,

            -- UNIQUE PRODUCTS
            COUNT(DISTINCT oi.product_id) AS total_unique_products,

            -- PRODUCT NAMES
            GROUP_CONCAT(
                DISTINCT p.name
                ORDER BY p.name ASC
            ) AS product_names

        FROM orders o

        LEFT JOIN order_items oi
            ON o.id = oi.order_id

        LEFT JOIN products p
            ON oi.product_id = p.id

        WHERE o.status != 'cancelled'

        GROUP BY DATE(o.created_at)

        ORDER BY sale_date DESC
    """, {})

    return rows


# =========================================================
# MONTHLY SALES REPORT
# =========================================================
async def get_monthly_sales_report():

    rows = await query_all("""
        SELECT

            DATE_FORMAT(o.created_at, '%Y-%m') AS month,

            COUNT(DISTINCT o.id) AS total_orders,

            COALESCE(SUM(o.total_amount), 0) AS total_sales,

            -- TOTAL UNITS SOLD
            COALESCE(SUM(oi.quantity), 0) AS total_units_sold,

            -- UNIQUE PRODUCTS
            COUNT(DISTINCT oi.product_id) AS total_unique_products,

            -- PRODUCT NAMES
            GROUP_CONCAT(
                DISTINCT p.name
                ORDER BY p.name ASC
            ) AS product_names

        FROM orders o

        LEFT JOIN order_items oi
            ON o.id = oi.order_id

        LEFT JOIN products p
            ON oi.product_id = p.id

        WHERE o.status != 'cancelled'

        GROUP BY DATE_FORMAT(o.created_at, '%Y-%m')

        ORDER BY month DESC
    """, {})

    return rows


# =========================================================
# TOP SELLING PRODUCTS
# =========================================================
async def get_top_selling_products():

    rows = await query_all("""
        SELECT

            p.id AS product_id,

            p.name AS product_name,

            COUNT(DISTINCT oi.order_id) AS total_orders,

            -- TOTAL UNITS SOLD
            COALESCE(SUM(oi.quantity), 0) AS total_units_sold,

            -- TOTAL SALES
            COALESCE(SUM(oi.total_price), 0) AS total_sales,

            -- AVERAGE PRICE
            COALESCE(AVG(oi.unit_price), 0) AS average_price

        FROM order_items oi

        LEFT JOIN products p
            ON oi.product_id = p.id

        LEFT JOIN orders o
            ON oi.order_id = o.id

        WHERE o.status != 'cancelled'

        GROUP BY p.id, p.name

        ORDER BY total_units_sold DESC

        LIMIT 10
    """, {})

    return rows
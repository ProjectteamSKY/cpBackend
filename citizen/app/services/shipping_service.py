from datetime import datetime
import json
import uuid

from sqlalchemy import text, true
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.utils.query_loader import load_queries
from app.integrations.shiprocket_client import ShiprocketClient

queries = load_queries()


shiprocket = ShiprocketClient()

def build_shiprocket_payload(order: dict):
    full_name = order.get("username", "Sriram Pandidurai")
    names = full_name.strip().split(" ", 1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else "NA"

    # ✅ Get valid pickup location from Shiprocket
    pickup_location_name = "Home"  # <-- replace with your real pickup location


    return {
        "order_id": order.get("id"),
        "order_date": str(order.get("created_at").date()),
        "pickup_location": pickup_location_name,  # use the valid pickup location

        # Billing info
        "billing_customer_name": "Sriram Pandidurai",
        "billing_first_name": "Sriram",
        "billing_last_name": "Pandidurai",
        "billing_address": "35, Indra Nagar, Itteri Road",
        "billing_city": "Palani",
        "billing_state": "Tamil Nadu",
        "billing_country": "India",
        "billing_pincode": "624601",
        "billing_email": "crazykidsri@email.com",
        "billing_phone": "7708012145",

        # Shipping info (same as billing)
        "shipping_customer_name": "Sriram Pandidurai",
        "shipping_first_name": "Sriram",
        "shipping_last_name": "Pandidurai",
        "shipping_address": "35, Indra Nagar, Itteri Road",
        "shipping_city": "Palani",
        "shipping_state": "Tamil Nadu",
        "shipping_country": "India",
        "shipping_pincode": "624601",
        "shipping_email": "crazykidsri@email.com",
        "shipping_phone": "7708012145",
        "shipping_is_billing": True,

        # Order items
        "order_items": [
            {
                "name": "CitizenPrints Order",
                "sku": "CP-001",
                "units": 1,
                "selling_price": float(order.get("total_amount", 0))
            }
        ],

        "payment_method": "COD",
        "sub_total": float(order.get("total_amount", 0)),
        "length": 10,
        "breadth": 10,
        "height": 5,
        "weight": 0.5
    }

async def create_order_service(order_id: str, session: AsyncSession):
    # 1️⃣ Fetch order from DB
    result = await session.execute(
        text("SELECT * FROM orders WHERE id=:id"),
        {"id": order_id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Order not found")

    order = dict(row._mapping)

    # 2️⃣ Build Shiprocket payload
    payload = build_shiprocket_payload(order)

    # 3️⃣ Call Shiprocket API
    try:
        response = shiprocket.create_order(payload)

        # 4️⃣ Print response immediately, fully, before any DB insert
        print("Shipment ID: - shipping_service.py:94", response["shipment_id"])

    except Exception as e:  
        raise HTTPException(500, f"Shiprocket API call failed: {str(e)}")

    # 5️⃣ Extract shipment_id safely
    shipment_id = response['shipment_id']

    print("Shipment ID: - shipping_service.py:102", shipment_id)

    if not shipment_id:
        raise HTTPException(
            500,
            f"Shiprocket did not return shipment_id. Response: {response}"
        )

    # 6️⃣ Insert into DB safely
    try:
        shipment_uuid = str(uuid.uuid4())
        await session.execute(
            text(
                """
                INSERT INTO shipments (id, order_id, shipment_id, shiprocket_order_id, awb_code, courier_name)
                VALUES (:id, :order_id, :shipment_id, :shiprocket_order_id, :awb_code, :courier_name)
                """
            ),
            {
                "id": shipment_uuid,
                "order_id": order_id,
                "shipment_id": shipment_id,
                "shiprocket_order_id": response["order_id"],  # <-- store Shiprocket order_id
                "awb_code": response.get("awb_code") or None,
                "courier_name": response.get("courier_name") or None,
            }
        )
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(500, f"DB insert failed: {str(e)}")

    # 7️⃣ Return full response for API client
    return {
        "status": "success",
        "shipment_id": shipment_id,
        "shiprocket_order_status": response["status"],
        "shiprocket_order_id": response["order_id"],
        "awb_code": response["awb_code"] or None,
        "courier_name": response["courier_name"] or None,
    }


# shipping_service.py
async def get_available_couriers_service(order_id: str, session: AsyncSession):
    # 1️⃣ Get Shiprocket order_id from DB
    result = await session.execute(
        text("SELECT shipment_id, shiprocket_order_id FROM shipments WHERE order_id = :order_id"),
        {"order_id": order_id}
    )
    row = result.fetchone()
    if not row or not row._mapping.get("shiprocket_order_id"):
        raise HTTPException(404, "Shipment not found or Shiprocket order not created")
    
    shiprocket_order_id = row._mapping["shiprocket_order_id"]

    # 2️⃣ Call Shiprocket API with order_id
    try:
        courier_response = shiprocket.get_courier_rates(shiprocket_order_id)
        print("couriers - shipping_service.py:161",courier_response)
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch courier rates: {str(e)}")

    # 3️⃣ Safely extract available courier companies
    couriers = courier_response.get("data", {}).get("available_courier_companies", [])
    
    print("couriers - shipping_service.py:168",couriers)
    # 4️⃣ Clean data for API response
    cleaned_couriers = [
        {
            "courier_id": c["courier_company_id"],
            "courier_name": c["courier_name"],
            "rate": c.get("rate"),
            "estimated_days": c.get("estimated_delivery_days"),
            "rating": c.get("rating"),
        }
        for c in couriers
    ]

    return {"status": "success", "couriers": cleaned_couriers}


async def assign_courier_service(order_id: str, courier_id: int, session: AsyncSession):

    # 1️⃣ Get shipment_id
    result = await session.execute(
        text("SELECT shipment_id FROM shipments WHERE order_id = :order_id"),
        {"order_id": order_id}
    )

    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipment_id = row._mapping["shipment_id"]

    if not shipment_id:
        raise HTTPException(status_code=400, detail="Shipment ID missing")

    # 2️⃣ Call Shiprocket API
    response = shiprocket.assign_courier(shipment_id, courier_id)

    if not response:
        raise HTTPException(status_code=500, detail="Courier assignment failed")

    # 3️⃣ Extract response values
    awb_code = response.get("awb_code")
    courier_name = response.get("courier_name")
    freight_charges = response.get("freight_charges")

    # 4️⃣ Update DB
    await session.execute(
        text("""
            UPDATE shipments
            SET courier_id = :courier_id,
                courier_name = :courier_name,
                awb_code = :awb_code,
                freight_charges = :freight_charges,
                updated_at = NOW()
            WHERE shipment_id = :shipment_id
        """),
        {
            "courier_id": courier_id,
            "courier_name": courier_name,
            "awb_code": awb_code,
            "freight_charges": freight_charges,
            "shipment_id": shipment_id
        }
    )

    await session.commit()

    return {
        "status": "success",
        "message": "Courier assigned successfully",
        "data": response
    }


async def download_label_service(order_id: str, session: AsyncSession):

    result = await session.execute(
        text("""
            SELECT shipment_id, label_url
            FROM shipments
            WHERE order_id = :order_id
        """),
        {"order_id": order_id}
    )

    row = result.fetchone()

    if not row:
        raise HTTPException(404, "Shipment not found")

    shipment_id = row._mapping["shipment_id"]
    existing_label = row._mapping["label_url"]

    # ✅ If label already stored, return it
    if existing_label:
        return {
            "status": "success",
            "label_url": existing_label
        }

    # Otherwise call Shiprocket
    label_url = shiprocket.download_label(shipment_id)

    await session.execute(
        text("""
            UPDATE shipments
            SET label_url = :label_url
            WHERE shipment_id = :shipment_id
        """),
        {"label_url": label_url, "shipment_id": shipment_id}
    )

    await session.commit()

    return {
        "status": "success",
        "label_url": label_url
    }


async def update_webhook_status_service(payload: dict, session: AsyncSession):

    # Log payload for debugging
    print("Shiprocket Webhook Payload:", payload)

    awb_code = payload.get("awb")
    order_status = (
        payload.get("current_status") or
        payload.get("shipment_status") or
        payload.get("status")
    )

    if not awb_code or not order_status:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    # Standardize status using mapping
    status_map = {
        "picked up": "shipped",
        "in transit": "shipped",
        "out for delivery": "shipped",
        "delivered": "delivered",
        "delivered to consignee": "delivered",
        "cancelled": "cancelled",
        "rto initiated": "rto"
    }

    order_status_clean = order_status.strip().lower()
    final_status = status_map.get(order_status_clean, order_status_clean)

    # Set delivered_at if delivered
    delivered_at = datetime.utcnow() if final_status == "delivered" else None

    # ------------------------
    # Update shipment
    # ------------------------
    await session.execute(
        text("""
            UPDATE shipments
            SET current_status = :status,
                delivered_at = COALESCE(:delivered_at, delivered_at),
                updated_at = NOW()
            WHERE awb_code = :awb_code
        """),
        {
            "status": final_status,
            "awb_code": awb_code,
            "delivered_at": delivered_at
        }
    )

    # ------------------------
    # Update order
    # ------------------------
    await session.execute(
        text("""
            UPDATE orders o
            JOIN shipments s ON s.order_id = o.id
            SET o.status = :status
            WHERE s.awb_code = :awb_code
        """),
        {
            "status": final_status,
            "awb_code": awb_code
        }
    )

    await session.commit()

    return {
        "status": "success",
        "message": f"Webhook processed: {final_status}"
    }

async def cancel_order_service(order_id: str, session: AsyncSession):
    """
    Cancel a shipment on Shiprocket and update DB
    """
    # 1️⃣ Get shipment_id from DB
    result = await session.execute(
        text("SELECT shipment_id, shiprocket_order_id FROM shipments WHERE order_id = :order_id"),
        {"order_id": order_id}
    )
    row = result.fetchone()
    if not row or not row._mapping.get("shiprocket_order_id"):
        raise HTTPException(404, "Shipment not found or Shiprocket order not created")

    shipment_id = row._mapping["shipment_id"]
    shiprocket_order_id = row._mapping["shiprocket_order_id"]

    # 2️⃣ Call Shiprocket API to cancel order
    try:
        response = shiprocket.cancel_order(shiprocket_order_id)
        print("Cancel response: - shipping_service.py:261", response)
    except Exception as e:
        raise HTTPException(500, f"Shiprocket cancel order failed: {str(e)}")

    # 3️⃣ Update DB status
    await session.execute(
        text(
            "UPDATE orders SET status = 'cancelled' WHERE id = :order_id"
        ),
        {"order_id": order_id}
    )
    await session.commit()

    return {"status": "success", "message": "Order cancelled", "shiprocket_response": response}


async def refund_order_service(order_id: str, session: AsyncSession, refund_amount: float = None):
    """
    Refund an order via Shiprocket
    """
    # 1️⃣ Get shipment info from DB
    result = await session.execute(
        text("SELECT shipment_id, shiprocket_order_id FROM shipments WHERE order_id = :order_id"),
        {"order_id": order_id}
    )
    row = result.fetchone()
    if not row or not row._mapping.get("shiprocket_order_id"):
        raise HTTPException(404, "Shipment not found or Shiprocket order not created")

    shiprocket_order_id = row._mapping["shiprocket_order_id"]

    # 2️⃣ Determine refund amount
    if refund_amount is None:
        # Default: full refund using order total
        result_order = await session.execute(
            text("SELECT total_amount FROM orders WHERE id = :order_id"),
            {"order_id": order_id}
        )
        order_row = result_order.fetchone()
        refund_amount = float(order_row._mapping["total_amount"])

    # 3️⃣ Call Shiprocket API to process refund
    try:
        response = shiprocket.refund_order(shiprocket_order_id, refund_amount)
        print("Refund response: - shipping_service.py:305", response)
    except Exception as e:
        raise HTTPException(500, f"Shiprocket refund failed: {str(e)}")

    # 4️⃣ Update DB order status if refund successful
    await session.execute(
        text(
            "UPDATE orders SET status = 'refunded' WHERE id = :order_id"
        ),
        {"order_id": order_id}
    )
    await session.commit()

    return {"status": "success", "message": "Order refunded", "refund_amount": refund_amount, "shiprocket_response": response}
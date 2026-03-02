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

        "payment_method": "Prepaid",
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
        print("Shipment ID: - shipping_service.py:93", response["shipment_id"])

    except Exception as e:  
        raise HTTPException(500, f"Shiprocket API call failed: {str(e)}")

    # 5️⃣ Extract shipment_id safely
    shipment_id = response['shipment_id']

    print("Shipment ID: - shipping_service.py:101", shipment_id)

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
        print("couriers - shipping_service.py:160",courier_response)
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch courier rates: {str(e)}")

    # 3️⃣ Safely extract available courier companies
    couriers = courier_response.get("data", {}).get("available_courier_companies", [])
    
    print("couriers - shipping_service.py:167",couriers)
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
    # Fetch shipment_id for the order
    result = await session.execute(
        text("SELECT shipment_id FROM shipments WHERE order_id = :order_id"),
        {"order_id": order_id}
    )
    row = result.fetchone()
    if not row or not row._mapping["shipment_id"]:
        raise HTTPException(404, "Shipment not found")
    
    shipment_id = row._mapping["shipment_id"]

    # Call Shiprocket client
    response = shiprocket.assign_courier(shipment_id, courier_id)
    
    # Optionally, you can update your DB to save assigned courier_id
    await session.execute(
        text("UPDATE shipments SET courier_id = :courier_id, updated_at = NOW() WHERE shipment_id = :shipment_id"),
        {"courier_id": courier_id, "shipment_id": shipment_id}
    )
    await session.commit()

    return {"status": "success", "assigned_courier": response}


async def download_label_service(order_id: str, session: AsyncSession):
    result = await session.execute(
        text("SELECT shipment_id FROM shipments WHERE order_id = :order_id"),
        {"order_id": order_id}
    )
    row = result.fetchone()
    if not row or not row._mapping["shipment_id"]:
        raise HTTPException(404, "Shipment not found")
    shipment_id = row._mapping["shipment_id"]

    label_pdf = shiprocket.download_label(shipment_id)
    return {"status": "success", "label_url": label_pdf}


async def update_webhook_status_service(payload: dict, session: AsyncSession):
    shipment_id = payload.get("shipment_id")
    order_status = payload.get("status")
    if not shipment_id or not order_status:
        raise HTTPException(400, "Invalid webhook payload")

    await session.execute(
        text(
            """
            UPDATE orders
            SET status = :status
            WHERE id = (SELECT order_id FROM shipments WHERE shipment_id = :shipment_id)
            """
        ),
        {"status": order_status, "shipment_id": shipment_id}
    )
    await session.commit()
    return {"status": "success", "message": "Webhook processed"}


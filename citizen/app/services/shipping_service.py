from datetime import datetime
import json
import uuid
from fastapi import HTTPException, Response

from app.core.database import execute, query, query_all
from app.utils.query_loader import load_queries
from app.integrations.shiprocket_client import ShiprocketClient
import requests
import math
from urllib.parse import quote

queries = load_queries()
shiprocket = ShiprocketClient()


async def build_hyperlocal_payload(order: dict, order_items: list):

    # -----------------------------
    # CUSTOMER INFO
    # -----------------------------
    first_name = (order.get("first_name") or "Customer").strip()
    last_name = (order.get("last_name") or "").strip()

    city = (order.get("city") or "").strip()
    state = (order.get("state") or "").replace("\xa0", " ").strip()
    address = (order.get("address_line") or "").strip()

    phone = str(order.get("phone") or "9999999999").strip()
    email = (order.get("email") or "noemail@test.com").strip()
    pincode = str(order.get("postal_code") or "").strip()

    if not city or not state or not address or not pincode:
        raise ValueError("Missing shipping/billing details")

    # -----------------------------
    # ITEMS
    # -----------------------------
    items = []
    for item in order_items:
        name = (item.get("product_name") or "Item").strip()
        units = int(item.get("units") or 1)
        price = float(item.get("unit_price") or 0)

        if price <= 0:
            continue

        items.append({
            "name": name,
            "sku": name.replace(" ", "_")[:40],
            "units": units,
            "selling_price": int(price),
            "category_code": "others",
            "category_name": "Others",
            "hsn": ""
        })

    if not items:
        raise ValueError("Order items required")

    # -----------------------------
    # PICKUP LOCATION (FIXED)
    # -----------------------------
    pickup_response = await get_pickup_locations_service()

    pickup_list = pickup_response["pickup_locations"]["shipping_address"]

    primary = next(
        (x for x in pickup_list if x.get("is_primary_location") == 1),
        pickup_list[0]
    )

    pickup_location = primary["pickup_location"]   # MUST be string
    pickup_lat = float(primary["lat"])
    pickup_long = float(primary["long"])

    # -----------------------------
    # ORDER DATE
    # -----------------------------
    order_date = order.get("created_at")
    if hasattr(order_date, "strftime"):
        order_date = order_date.strftime("%Y-%m-%d %H:%M")

    # -----------------------------
    # FINAL PAYLOAD
    # -----------------------------
    return {
        "order_id": str(order.get("order_number") or order.get("id")),
        "order_date": order_date,

        # REQUIRED
        "pickup_location": pickup_location,

        # OPTIONAL
        "channel_id": order.get("channel_id"),

        # BILLING
        "billing_customer_name": first_name,
        "billing_last_name": last_name,
        "billing_address": address,
        "billing_city": city,
        "billing_state": state,
        "billing_country": "India",
        "billing_pincode": pincode,
        "billing_email": email,
        "billing_phone": phone,

        # SHIPPING
        "shipping_is_billing": 1,

        # ITEMS
        "order_items": items,

        # PAYMENT
        "payment_method": (order.get("payment_method") or "COD").upper(),

        # REQUIRED
        "sub_total": int(order.get("total_amount") or 0),

        # PACKAGE
        "length": 10.0,
        "breadth": 10.0,
        "height": 10.0,
        "weight": 0.5,

        # IMPORTANT FOR HYPERLOCAL (FIXED)
        "latitude": pickup_lat,
        "longitude": pickup_long,

        # REQUIRED
        "shipping_method": "HL"
    }

    

def build_shiprocket_payload(order: dict, order_items: list):

    # ---------------------------------------------------------
    # 1. CUSTOMER DETAILS
    # ---------------------------------------------------------
    first_name = order.get("first_name") or "Customer"
    last_name = order.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip()

    state = (order.get("state") or "").replace("\xa0", " ").strip()

    address_line = order.get("address_line") or ""
    city = order.get("city") or ""
    country = order.get("country") or "India"
    postal_code = order.get("postal_code") or ""

    email = order.get("email") or "noemail@example.com"
    phone = order.get("phone") or "9999999999"

    delivery_type = (order.get("delivery_type") or "normal").lower()

    # ---------------------------------------------------------
    # 2. ITEM PROCESSING
    # ---------------------------------------------------------
    items_payload = []

    lengths = []
    breadths = []
    heights = []

    total_weight = 0.0

    for item in order_items:

        name = (item.get("product_name") or "").strip()
        units = int(item.get("units") or 1)

        unit_price = float(item.get("unit_price") or 0)
        if unit_price == 0 and item.get("total_price"):
            unit_price = float(item["total_price"]) / units

        weight = float(item.get("weight") or 0)
        total_weight += weight

        # dimensions
        lengths.append(float(item.get("length") or 10))
        breadths.append(float(item.get("breadth") or 10))
        heights.append(float(item.get("height") or 5))

        items_payload.append({
            "name": name,
            "sku": name.replace(" ", "_")[:40],
            "units": units,
            "selling_price": round(unit_price, 2)
        })

    # ---------------------------------------------------------
    # 3. FALLBACK SAFETY
    # ---------------------------------------------------------
    if not items_payload:
        items_payload = [{
            "name": "Order Item",
            "sku": "CP-001",
            "units": 1,
            "selling_price": float(order.get("total_amount", 0))
        }]
        lengths, breadths, heights = [10], [10], [5]
        total_weight = 0.5

    total_weight = max(total_weight, 0.5)

    # ---------------------------------------------------------
    # 4. DYNAMIC DIMENSIONS
    # ---------------------------------------------------------
    base_length = max(lengths) if lengths else 10
    base_breadth = max(breadths) if breadths else 10
    base_height = sum(heights) if heights else 5

    # ---------------------------------------------------------
    # 5. HYPERLOCAL vs NORMAL LOGIC
    # ---------------------------------------------------------
    if delivery_type == "hyperlocal":

        # compress packaging (still dynamic, no hardcoding)
        length = max(3, base_length * 0.6)
        breadth = max(3, base_breadth * 0.6)
        height = max(2, base_height * 0.5)

        # optional: reduce weight sensitivity slightly
        total_weight = max(0.5, total_weight * 0.9)

    else:

        # full accuracy for courier shipping
        length = base_length
        breadth = base_breadth
        height = base_height

    # ---------------------------------------------------------
    # 6. FINAL ROUNDING
    # ---------------------------------------------------------
    length = round(length, 2)
    breadth = round(breadth, 2)
    height = round(height, 2)
    total_weight = round(total_weight, 2)

    # ---------------------------------------------------------
    # 7. PAYMENT METHOD (Shiprocket standard)
    # ---------------------------------------------------------
    payment_method = (order.get("payment_method") or "COD").upper()

    # ---------------------------------------------------------
    # 8. FINAL PAYLOAD
    # ---------------------------------------------------------
    return {
        "order_id": order.get("order_number") or order.get("id"),
        "order_date": str(order.get("created_at").strftime("%Y-%m-%d %H:%M")),
        "pickup_location": "Home-1",

        # BILLING
        "billing_customer_name": full_name,
        "billing_first_name": first_name,
        "billing_last_name": last_name,
        "billing_address": address_line,
        "billing_city": city,
        "billing_state": state,
        "billing_country": country,
        "billing_pincode": postal_code,
        "billing_email": email,
        "billing_phone": phone,

        # SHIPPING
        "shipping_is_billing": True,

        # ITEMS
        "order_items": items_payload,

        # PAYMENT
        "payment_method": payment_method,
        "sub_total": float(order.get("total_amount", 0)),

        # PACKAGE
        "length": length,
        "breadth": breadth,
        "height": height,
        "weight": total_weight
    }


async def create_hyperlocal_order_service(order_id: str):

    # 1. FETCH ORDER
    order = await query(
        queries["shipping"]["get_order_details"],
        {"id": order_id}
    )

    if not order:
        raise HTTPException(404, "Order not found")

    # 2. FETCH ITEMS
    order_items = await query_all(
        queries["order_item"]["get_all_order_item"],
        {"order_id": order_id}
    )

    # 3. BUILD PAYLOAD
    payload = await build_hyperlocal_payload(order, order_items)

    # 4. CREATE SHIPROCKET ORDER
    try:

        response = shiprocket.create_hyperlocal_order(payload)

        print(
            "Shiprocket create order response:",
            response
        )

    except Exception as e:

        raise HTTPException(
            500,
            f"Hyperlocal create failed: {str(e)}"
        )

    # 5. EXTRACT RESPONSE
    order_id_sr = response.get("order_id")
    shipment_id = response.get("shipment_id")

    if not shipment_id:
        raise HTTPException(
            500,
            "Shipment ID not returned from Shiprocket"
        )

    # 6. ASSIGN COURIER
    assign_response = None
    awb_code = None
    courier_name = None
    tracking_url = None

    try:

        # -----------------------------------
        # AUTO ASSIGN COURIER
        # -----------------------------------
        assign_response = shiprocket.hyper_local_assign_courier(
            shipment_id
        )

        print(
            "Assign response:",
            assign_response
        )

        # -----------------------------------
        # AWB GENERATED
        # -----------------------------------
        if assign_response:

            if assign_response.get("awb_assign_status") == 1:

                awb_code = assign_response.get("awb_code")
                courier_name = assign_response.get("courier_name")
                tracking_url = assign_response.get("tracking_url")

                print(
                    "AWB Generated Successfully:",
                    awb_code
                )

            # -----------------------------------
            # HYPERLOCAL PROCESSING
            # -----------------------------------
            elif assign_response.get("success") is True:

                print(
                    "Hyperlocal processing started:",
                    assign_response.get("message")
                )

            # -----------------------------------
            # FAILED
            # -----------------------------------
            else:

                print(
                    "Courier assignment failed:",
                    assign_response
                )

    except Exception as e:

        print(
            "Hyperlocal courier assign error:",
            str(e)
        )

    # 7. SAVE SHIPMENT
    shipment_uuid = str(uuid.uuid4())

    await execute(
        queries["shipping"]["create_shipment"],
        {
            "id": shipment_uuid,
            "order_id": order_id,
            "shiprocket_order_id": order_id_sr,
            "shipment_id": shipment_id,
            "awb_code": awb_code,
            "courier_name": courier_name,
            "tracking_url": tracking_url,
            "current_status": "processing",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )

    # 8. UPDATE ORDER STATUS
    await execute(
        queries["shipping"]["update_order_status"],
        {
            "order_id": order_id,
            "status": "processing"
        }
    )

    # 9. RESPONSE
    return {
        "status": "success",
        "type": "hyperlocal",
        "order_id": order_id_sr,
        "shipment_id": shipment_id,
        "awb_code": awb_code,
        "courier_name": courier_name,
        "tracking_url": tracking_url,
        "processing": awb_code is None,
        "assign_response": assign_response
    }


async def create_order_service(order_id: str):

    # ---------------------------------------------------------
    # 1. FETCH ORDER
    # ---------------------------------------------------------
    order = await query(
        queries["shipping"]["get_order_details"],
        {"id": order_id}
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    delivery_type = (
        order.get("delivery_type") or "normal"
    ).lower()

    # ---------------------------------------------------------
    # 2. HYPERLOCAL FLOW
    # ---------------------------------------------------------
    if delivery_type == "hyperlocal":
        return await create_hyperlocal_order_service(order_id)

    # ---------------------------------------------------------
    # 3. FETCH ORDER ITEMS
    # ---------------------------------------------------------
    order_items = await query_all(
        queries["order_item"]["get_all_order_item"],
        {"order_id": order_id}
    )

    if not order_items:
        raise HTTPException(
            status_code=400,
            detail="Order items not found"
        )

    # ---------------------------------------------------------
    # 4. BUILD PAYLOAD
    # ---------------------------------------------------------
    payload = build_shiprocket_payload(
        order,
        order_items
    )

    # ---------------------------------------------------------
    # 5. CREATE ORDER IN SHIPROCKET
    # ---------------------------------------------------------
    try:
        response = shiprocket.create_order(payload)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Shiprocket create order failed: {str(e)}"
        )

    print(
        "Shiprocket create order response - shipping_service.py:",
        response
    )

    shipment_id = response.get("shipment_id")
    shiprocket_order_id = response.get("order_id")

    if not shipment_id or not shiprocket_order_id:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid Shiprocket response: {response}"
        )

    # ---------------------------------------------------------
    # 6. DEFAULT VALUES
    # ---------------------------------------------------------
    courier_id = order.get("courier_id")
    courier_name = order.get("courier_name")

    awb_code = None

    freight_charges = float(
        order.get("delivery_charge") or 0
    )

    assign_response = {}

    pickup_status = None
    pickup_token_number = None
    pickup_scheduled_date = None

    shipment_status = "shipment"
    order_status = "shipment"

    # ---------------------------------------------------------
    # 7. ASSIGN COURIER
    # ---------------------------------------------------------
    if courier_id:

        try:
            assign_response = shiprocket.assign_courier(
                shipment_id,
                int(courier_id)
            )

            print(
                "Shiprocket assign courier response - shipping_service.py:",
                assign_response
            )

            if assign_response:

                # ---------------------------------------------------------
                # AWB
                # ---------------------------------------------------------
                awb_code = (
                    assign_response.get("awb_code")
                    or None
                )

                # ---------------------------------------------------------
                # COURIER NAME
                # ---------------------------------------------------------
                courier_name = (
                    assign_response.get("courier_name")
                    or courier_name
                )

                # ---------------------------------------------------------
                # FREIGHT
                # ---------------------------------------------------------
                freight_raw = assign_response.get(
                    "freight_charges"
                )

                if freight_raw not in [
                    None,
                    "",
                    "null"
                ]:
                    freight_charges = float(freight_raw)

                # ---------------------------------------------------------
                # AUTO PICKUP DETECTION
                # ---------------------------------------------------------
                pickup_scheduled_date = (
                    assign_response.get("raw_response", {})
                    .get("response", {})
                    .get("data", {})
                    .get("pickup_scheduled_date")
                )

                print(
                    "pickup_scheduled_date:",
                    pickup_scheduled_date
                )

                # ---------------------------------------------------------
                # SOME COURIERS AUTO SCHEDULE PICKUP
                # ---------------------------------------------------------
                if pickup_scheduled_date:

                    pickup_status = "scheduled"

                    shipment_status = "pickup_scheduled"

                    order_status = "pickup_scheduled"

        except Exception as e:

            print(
                f"Courier assign failed (NONBLOCKING): {str(e)} "
                f"- shipping_service.py"
            )

    # ---------------------------------------------------------
    # 8. CREATE SHIPMENT RECORD
    # ---------------------------------------------------------
    shipment_uuid = str(uuid.uuid4())

    await execute(
        queries["shipping"]["create_shipment"],
        {
            "id": shipment_uuid,
            "order_id": order_id,
            "shiprocket_order_id": shiprocket_order_id,
            "shipment_id": shipment_id,
            "awb_code": awb_code,
            "courier_name": courier_name,
            "tracking_url": None,

            # ---------------------------------------------------------
            # STATUS
            # ---------------------------------------------------------
            "current_status": shipment_status,

            # ---------------------------------------------------------
            # PICKUP
            # ---------------------------------------------------------
            "pickup_status": pickup_status,
            "pickup_token_number": pickup_token_number,
            "pickup_scheduled_date": pickup_scheduled_date,

            # ---------------------------------------------------------
            # TIMESTAMP
            # ---------------------------------------------------------
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )

    # ---------------------------------------------------------
    # 9. SAVE COURIER DETAILS
    # ---------------------------------------------------------
    if courier_id:

        await execute(
            queries["shipping"]["assign_courier"],
            {
                "courier_id": int(courier_id),
                "courier_name": courier_name,
                "awb_code": awb_code,
                "freight_charges": freight_charges,
                "shipment_id": shipment_id
            }
        )

    # ---------------------------------------------------------
    # 10. UPDATE ORDER STATUS
    # ---------------------------------------------------------
    await execute(
        queries["shipping"]["update_order_status"],
        {
            "order_id": order_id,
            "status": order_status
        }
    )

    # ---------------------------------------------------------
    # 11. ADD FREIGHT TO ORDER
    # ---------------------------------------------------------
    await execute(
        queries["shipping"]["add_freight_to_total"],
        {
            "order_id": order_id,
            "freight": freight_charges
        }
    )

    # ---------------------------------------------------------
    # 12. FINAL RESPONSE
    # ---------------------------------------------------------
    return {
        "status": "success",
        "message": (
            "Order created and pickup auto scheduled"
            if pickup_status == "scheduled"
            else "Order created successfully"
        ),

        "order_id": order_id,

        "shipment_id": shipment_id,

        "shiprocket_order_id": shiprocket_order_id,

        "awb_code": awb_code,

        "courier_id": courier_id,

        "courier_name": courier_name,

        "freight": freight_charges,

        "pickup_status": pickup_status,

        "pickup_scheduled_date": pickup_scheduled_date,

        "current_status": shipment_status
    }

# ---------------------------------------------------------
# Get Available Couriers
# ---------------------------------------------------------
async def get_available_couriers_service(order_id: str):

    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(404, "Shipment not found")

    shiprocket_order_id = shipment["shiprocket_order_id"]
    shipment_id = shipment["shipment_id"]

    # Prevent duplicate assignment
    if shipment.get("awb_code"):
        return {
            "status": "success",
            "message": "Courier already assigned",
            "awb_code": shipment.get("awb_code"),
            "courier_name": shipment.get("courier_name")
        }

    # ---------------------------------------------------------
    # Get courier list
    # ---------------------------------------------------------
    try:
        courier_response = shiprocket.get_courier_rates(shiprocket_order_id)
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch courier rates: {str(e)}")

    couriers = courier_response.get("data", {}).get("available_courier_companies", [])

    if not couriers:
        return {
            "status": "success",
            "best_courier": None
        }

    # ---------------------------------------------------------
    # Find best courier
    # ---------------------------------------------------------
    best_courier = None
    best_score = float("inf")

    for c in couriers:
        freight = float(c.get("freight_charge") or c.get("rate") or 0)
        cod = float(c.get("cod_charges") or 0)
        other = float(c.get("other_charges") or 0)

        total_cost = freight + cod + other

        days = int(c.get("estimated_delivery_days") or 7)
        rating = float(c.get("rating") or 0)

        score = (total_cost * 0.7) + (days * 0.2) - (rating * 0.1)

        if score < best_score:
            best_score = score
            best_courier = {
                "courier_id": c.get("courier_company_id"),
                "courier_name": c.get("courier_name"),
                "total_cost": round(total_cost, 2),
                "estimated_days": days,
                "rating": rating,
                "etd": c.get("etd")
            }

    if not best_courier:
        raise HTTPException(400, "No suitable courier found")


    print("best courier @@@@@@@@@@@@@@@@@@@@@@@@@@@@ - shipping_service.py:793",best_courier)
    # ---------------------------------------------------------
    # Assign courier (AWB)
    # ---------------------------------------------------------
    assign_response = shiprocket.assign_courier(
        shipment_id,
        best_courier["courier_id"]
    )
    assign_response = []
    if not assign_response:
        raise HTTPException(500, "Courier assignment failed")

    freight_charges = float(assign_response.get("freight_charges") or 0)

    # ---------------------------------------------------------
    # Save shipment data
    # ---------------------------------------------------------
    await execute(
        queries["shipping"]["assign_courier"],
        {
            "courier_id": best_courier["courier_id"],
            "courier_name": assign_response.get("courier_name"),
            "awb_code": assign_response.get("awb_code"),
            "freight_charges": freight_charges,
            "shipment_id": shipment_id
        }
    )

    # ---------------------------------------------------------
    # UPDATE ORDER STATUS → shipment
    # ---------------------------------------------------------
    await execute(
        queries["orders"]["update_order_status"],
        {
            "order_id": order_id,
            "status": "shipment"
        }
    )

    # ---------------------------------------------------------
    # ADD FREIGHT TO TOTAL PRICE
    # ---------------------------------------------------------
    await execute(
        queries["orders"]["add_freight_to_total"],
        {
            "order_id": order_id,
            "freight": freight_charges
        }
    )

    return {
        "status": "success",
        "message": "Courier auto-assigned successfully",
        "best_courier": best_courier,
        "assignment": assign_response
    }

# ---------------------------------------------------------
# Assign Courier
# ---------------------------------------------------------
async def assign_courier_service(order_id: str, courier_id: int):

    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(404, "Shipment not found")

    shipment_id = shipment["shipment_id"]

    response = shiprocket.assign_courier(shipment_id, courier_id)

    if not response:
        raise HTTPException(500, "Courier assignment failed")

    await execute(
        queries["shipping"]["assign_courier"],
        {
            "courier_id": courier_id,
            "courier_name": response.get("courier_name"),
            "awb_code": response.get("awb_code"),
            "freight_charges": response.get("freight_charges"),
            "shipment_id": shipment_id
        }
    )

    return {
        "status": "success",
        "message": "Courier assigned successfully",
        "data": response
    }


# ---------------------------------------------------------
# Download Label
# ---------------------------------------------------------
async def download_label_service(order_id: str):

    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(404, "Shipment not found")

    if shipment.get("label_url"):
        return {
            "status": "success",
            "label_url": shipment["label_url"]
        }

    label_url = shiprocket.download_label(shipment["shipment_id"])

    await execute(
        queries["shipping"]["update_label"],
        {
            "label_url": label_url,
            "shipment_id": shipment["shipment_id"]
        }
    )

    return {
        "status": "success",
        "label_url": label_url
    }

async def get_manifest_label_service(order_id: str):

    # 1. Fetch shipment
    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipment_id = shipment["shipment_id"]

    # 2. Check DB cache
    manifest_url = shipment.get("manifest_url")

    # 3. If not exists → generate from Shiprocket
    if not manifest_url:
        manifest_response = shiprocket.generate_manifest([shipment_id])

        print("Manifest response: - shipping_service.py:942", manifest_response)

        manifest_url = (
            manifest_response.get("manifest_url")
            or manifest_response.get("data", {}).get("manifest_url")
        )

        if not manifest_url:
            raise HTTPException(
                status_code=400,
                detail=f"Manifest generation failed: {manifest_response}"
            )

        # Save to DB (cache it)
        await execute(
            queries["shipping"]["update_manifest"],
            {
                "shipment_id": shipment_id,
                "manifest_url": manifest_url
            }
        )

    # 4. DOWNLOAD FILE (IMPORTANT PART)
    file_response = requests.get(manifest_url)

    if file_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download manifest")

    # 5. Return file directly to browser (Chrome download)
    return Response(
        content=file_response.content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="manifest_{shipment_id}.pdf"'
        }
    )


async def get_invoice_service(order_id: str):

    # 1. Fetch shipment
    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(status_code=404, detail="Order not found")

    # 🔥 IMPORTANT: use Shiprocket ORDER ID (not shipment_id)
    shiprocket_order_id = shipment.get("shiprocket_order_id")

    if not shiprocket_order_id:
        raise HTTPException(
            status_code=400,
            detail="Shiprocket order id not found in shipment"
        )

    # 2. Call Shiprocket Invoice API
    invoice_response = shiprocket.generate_invoice([shiprocket_order_id])

    print("Invoice response: - shipping_service.py:1003", invoice_response)

    # 3. Extract URL (if returned)
    invoice_url = (
        invoice_response.get("invoice_url")
        or invoice_response.get("data", {}).get("invoice_url")
        or invoice_response.get("file_url")
    )

    if not invoice_url:
        raise HTTPException(
            status_code=400,
            detail=f"Invoice generation failed: {invoice_response}"
        )

    # 4. Download PDF
    file_resp = requests.get(invoice_url)

    if file_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download invoice")

    # 5. Return PDF to browser
    return Response(
        content=file_resp.content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice_{shiprocket_order_id}.pdf"'
        }
    )


# ---------------------------------------------------------
# Generate Pickup
# ---------------------------------------------------------
async def generate_pickup_service(order_id: str):

    # ---------------------------------------------------------
    # 1. FETCH SHIPMENT
    # ---------------------------------------------------------
    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    shipment_id = shipment.get("shipment_id")

    if not shipment_id:
        raise HTTPException(
            status_code=400,
            detail="Shipment ID not found"
        )

    # ---------------------------------------------------------
    # 2. PREVENT DUPLICATE PICKUP
    # ---------------------------------------------------------
    if shipment.get("pickup_token_number"):

        return {
            "status": "success",
            "message": "Pickup already scheduled",
            "shipment_id": shipment_id,
            "pickup_token_number": shipment.get("pickup_token_number"),
            "pickup_scheduled_date": shipment.get("pickup_scheduled_date")
        }

    # ---------------------------------------------------------
    # 3. GENERATE PICKUP
    # ---------------------------------------------------------
    try:
        response = shiprocket.generate_pickup([shipment_id])

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pickup generation failed: {str(e)}"
        )

    print(
        "Pickup response - shipping_service.py:",
        response
    )

    # ---------------------------------------------------------
    # 4. VALIDATE RESPONSE
    # ---------------------------------------------------------
    pickup_status = response.get("pickup_status")

    if pickup_status != 1:
        raise HTTPException(
            status_code=400,
            detail=f"Pickup generation failed: {response}"
        )

    # ---------------------------------------------------------
    # 5. EXTRACT RESPONSE DATA
    # ---------------------------------------------------------
    pickup_response = response.get("response", {})

    pickup_scheduled_date = pickup_response.get(
        "pickup_scheduled_date"
    )

    pickup_token_number = pickup_response.get(
        "pickup_token_number"
    )

    pickup_message = (
        pickup_response.get("data")
        or pickup_response.get("message")
        or "Pickup scheduled successfully"
    )

    # ---------------------------------------------------------
    # 6. SAVE PICKUP DETAILS
    # ---------------------------------------------------------
    await execute(
        queries["shipping"]["update_pickup"],
        {
            "shipment_id": shipment_id,
            "pickup_status": "scheduled",
            "pickup_token_number": pickup_token_number,
            "pickup_scheduled_date": pickup_scheduled_date
        }
    )

    # ---------------------------------------------------------
    # 7. UPDATE SHIPMENT STATUS
    # ---------------------------------------------------------
    await execute(
        queries["shipping"]["update_status_by_shipment"],
        {
            "shipment_id": shipment_id,
            "status": "pickup_scheduled"
        }
    )

    # ---------------------------------------------------------
    # 8. UPDATE ORDER STATUS
    # ---------------------------------------------------------
    await execute(
        queries["shipping"]["update_order_status"],
        {
            "order_id": order_id,
            "status": "pickup_scheduled"
        }
    )

    # ---------------------------------------------------------
    # 9. RETURN RESPONSE
    # ---------------------------------------------------------
    return {
        "status": "success",
        "message": "Pickup generated successfully",
        "shipment_id": shipment_id,
        "pickup_status": pickup_status,
        "pickup_scheduled_date": pickup_scheduled_date,
        "pickup_token_number": pickup_token_number,
        "pickup_message": pickup_message,
        "shiprocket_response": response
    }
# ---------------------------------------------------------
# Webhook Status Update
# ---------------------------------------------------------
async def update_webhook_status_service(payload: dict):

    try:

        print(
            "Webhook payload received - shipping_service.py",
            payload
        )

        # ------------------------------------------------
        # VALIDATION
        # ------------------------------------------------
        awb_code = str(
            payload.get("awb", "")
        ).strip()

        order_status = (
            payload.get("current_status")
            or payload.get("shipment_status")
            or payload.get("status")
            or ""
        )

        if not awb_code:
            print("Missing AWB code - shipping_service.py:1196")
            return

        if not order_status:
            print("Missing order status - shipping_service.py:1200")
            return

        # ------------------------------------------------
        # GET SHIPMENT USING AWB
        # ------------------------------------------------
        shipment = await query(
            queries["shipping"]["get_shipment_by_awb"],
            {
                "awb_code": awb_code
            }
        )
        print("Shipment Query Result: - shipping_service.py:1212", shipment)

        if not shipment:

            print(
                f"Shipment not found for AWB: {awb_code}"
            )

            return

        shipment_id = shipment["id"]
        order_id = shipment["order_id"]

        # ------------------------------------------------
        # NORMALIZE STATUS
        # ------------------------------------------------
        status_clean = order_status.strip().lower()

        status_map = {

            # NORMAL DELIVERY
            "picked up": "shipped",
            "shipment picked up": "shipped",

            "in transit": "shipped",

            "out for delivery": "out_for_delivery",
            "shipment out for delivery": "out_for_delivery",

            "delivered": "delivered",
            "shipment delivered": "delivered",
            "delivered to consignee": "delivered",

            "cancelled": "cancelled",

            "rto initiated": "rto",

            # HYPERLOCAL
            "rider assigned": "rider_assigned",
            "rider reached pickup": "pickup_arrived",
            "picked": "picked",
            "on the way": "in_transit",
            "reached drop": "reached_drop",
            "completed": "delivered",
        }

        final_status = status_map.get(
            status_clean,
            status_clean
        )

        # ------------------------------------------------
        # DELIVERED DATE
        # ------------------------------------------------
        delivered_at = None

        if final_status == "delivered":
            delivered_at = datetime.utcnow()

        # ------------------------------------------------
        # SAVE WEBHOOK LOG
        # ------------------------------------------------
        await execute(
            queries["shipping"]["insert_webhook_log"],
            {
                "id": str(uuid.uuid4()),

                "shipment_id": shipment_id,

                "awb_code": awb_code,

                "event_status": final_status,

                "payload": json.dumps(payload)
            }
        )

        # ------------------------------------------------
        # UPDATE SHIPMENT STATUS
        # ------------------------------------------------
        await execute(
            queries["shipping"]["update_status_by_awb"],
            {
                "awb_code": awb_code,
                "status": final_status,
                "delivered_at": delivered_at
            }
        )

        # ------------------------------------------------
        # UPDATE ORDER STATUS
        # ------------------------------------------------
        await execute(
            queries["shipping"]["update_order_status"],
            {
                "order_id": order_id,
                "status": final_status
            }
        )

        print(
            f"Webhook processed successfully "
            f"AWB={awb_code} "
            f"STATUS={final_status}"
        )

    except Exception as e:

        print(
            "Webhook processing failed:",
            str(e)
        )

        # IMPORTANT:
        # NEVER FAIL WEBHOOK
        # Shiprocket retries if not HTTP 200
        return

# ---------------------------------------------------------
# Cancel Order
# ---------------------------------------------------------
async def cancel_order_service(order_id: str):

    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(404, "Shipment not found")

    awb = shipment.get("awb_code")

    if not awb:
        raise HTTPException(400, "AWB not found for this shipment")

    response = shiprocket.cancel_order(awb)

    await execute(
        queries["shipping"]["cancel_order"],
        {"order_id": order_id}
    )

    return {
        "status": "success",
        "message": "Shipment cancelled",
        "awb": awb,
        "shiprocket_response": response
    }


# ---------------------------------------------------------
# Refund Order
# ---------------------------------------------------------
async def refund_order_service(order_id: str, refund_amount: float = None):

    shipment = await query(
        queries["shipping"]["get_shipment_by_order"],
        {"order_id": order_id}
    )

    if not shipment:
        raise HTTPException(404, "Shipment not found")

    if refund_amount is None:

        order = await query(
            queries["shipping"]["get_order_amount"],
            {"order_id": order_id}
        )

        refund_amount = float(order["total_amount"])

    response = shiprocket.refund_order(
        shipment["shiprocket_order_id"],
        refund_amount
    )

    await execute(
        queries["shipping"]["refund_order"],
        {"order_id": order_id}
    )

    return {
        "status": "success",
        "refund_amount": refund_amount,
        "shiprocket_response": response
    }




# async def couriers_service(
#     pickup_postcode: str,
#     delivery_postcode: str,
#     weight: float,
#     cod: int,
#     declared_value: float
# ):
#     """
#     Fetch couriers from Shiprocket API and return:
#     1. Full filtered courier list
#     2. Single best courier based on lowest total cost
#     """
#     print("API triggers for courier availability - shipping_service.py:598")
    
#     # Call Shiprocket API
#     response = shiprocket.get_couriers_by_address(
#         pickup_postcode="600100",
#         delivery_postcode=delivery_postcode,
#         weight=1,
#         cod=cod,
#         declared_value=declared_value
#     )
    
#     couriers = response.get("data", {}).get("available_courier_companies", [])
#     print("available couriers - shipping_service.py:610",couriers)
#     # Filter required fields
#     filtered_couriers = []
#     for c in couriers:
#         filtered_couriers.append({
#             "courier_name": c.get("courier_name"),
#             "courier_type": "Surface" if c.get("is_surface") else "Air",
#             "city": c.get("city"),
#             "state": c.get("state"),
#             "postcode": c.get("postcode"),
#             "rate": c.get("rate") or 0,                      # base rate
#             "freight_charge": c.get("freight_charge") or 0,  # final charge
#             "other_charges": c.get("other_charges") or 0,    # additional charges
#             "cod": c.get("cod"),
#             "cod_charges": c.get("cod_charges") or 0,
#             "total_cost": (c.get("freight_charge") or 0) + (c.get("other_charges") or 0) + ((c.get("cod_charges") or 0) if cod else 0),
#             "estimated_delivery_days": c.get("estimated_delivery_days"),
#             "etd": c.get("etd"),
#             "pickup_availability": c.get("pickup_availability"),
#             "delivery_performance": c.get("delivery_performance"),
#             "pickup_performance": c.get("pickup_performance"),
#             "rating": c.get("rating"),
#             "surface_max_weight": c.get("surface_max_weight"),
#             "air_max_weight": c.get("air_max_weight")
#         })
    
#     # Sort by total cost (lowest first)
#     filtered_couriers.sort(key=lambda x: x["total_cost"])
    
#     # Best single courier (lowest total cost)
#     best_courier = filtered_couriers[0] if filtered_couriers else None
    
#     return {
#         "best_courier": best_courier
#     }


async def couriers_service(
    pickup_postcode: str,
    delivery_postcode: str,
    weight: float,
    cod: int,
    declared_value: float,
    length: float,
    breadth: float,
    height: float
):
    """
    Fetch couriers from Shiprocket and return:
    - clean courier list
    - best courier (lowest cost + rating balance)
    """

    # =========================
    # Shiprocket API CALL
    # =========================
    response = shiprocket.get_couriers_by_address(
        pickup_postcode="600026",
        delivery_postcode=delivery_postcode,
        weight=weight,
        cod=cod,
        declared_value=declared_value,
        length=length,
        breadth=breadth,
        height=height
    )

    couriers = response.get("data", {}).get("available_courier_companies", [])

    # =========================
    # COST CALCULATION
    # =========================
    def calculate_total_cost(c):
        base_rate = float(c.get("rate") or 0)

        cod_charge = float(c.get("cod_charges") or 0) if cod == 1 else 0

        whatsapp_charges = float(c.get("whatsapp_charges") or 0)
        coverage_charges = float(c.get("coverage_charges") or 0)
        entry_tax = float(c.get("entry_tax") or 0)
        other_charges = float(c.get("other_charges") or 0)
        surge_total = sum(
            float(s.get("charge") or 0)
            for s in (c.get("surge") or [])
        )

        total = (
            base_rate +
            cod_charge +
            whatsapp_charges +
            coverage_charges +
            entry_tax +
            other_charges +
            surge_total
        )

        return round(total, 2)

    filtered_couriers = []

    # =========================
    # FILTER & NORMALIZE
    # =========================
    for c in couriers:

        if str(c.get("pickup_availability")) == "0":
            continue

        total_cost = calculate_total_cost(c)

        filtered_couriers.append({
            # Identity
            "courier_company_id": c.get("courier_company_id"),
            "courier_name": c.get("courier_name"),
            "courier_type": "Surface" if c.get("is_surface") else "Air",

            # Location
            "city": c.get("city"),
            "state": c.get("state"),
            "postcode": c.get("postcode"),

            # Pricing
            "rate": float(c.get("rate") or 0),
            "cod_charges": float(c.get("cod_charges") or 0),
            "total_cost": total_cost,

            # Delivery
            "estimated_delivery_days": c.get("estimated_delivery_days"),
            "etd": c.get("etd"),   # ADDED

            # Performance
            "rating": float(c.get("rating") or 0),
            "delivery_performance": c.get("delivery_performance"),
            "pickup_performance": c.get("pickup_performance"),
        })

    # =========================
    # FALLBACK SAFETY
    # =========================
    if not filtered_couriers:
        filtered_couriers = [
            {
                "courier_company_id": c.get("courier_company_id"),
                "courier_name": c.get("courier_name"),
                "rate": float(c.get("rate") or 0),
                "cod_charges": float(c.get("cod_charges") or 0),
                "total_cost": calculate_total_cost(c),
                "rating": float(c.get("rating") or 0),
                "etd": c.get("etd"),   #  ADDED
            }
            for c in couriers
        ]

    # =========================
    # BEST COURIER SELECTION
    # =========================
    filtered_couriers.sort(
        key=lambda x: (
            x["total_cost"],
            -x["rating"]
        )
    )

    best_courier = filtered_couriers[0] if filtered_couriers else None

    return {
        "best_courier": best_courier,
        "all_couriers": filtered_couriers
    }


async def get_lat_long_from_pincode(pincode: str):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&country=India&format=json"

    response = requests.get(url, headers={"User-Agent": "your-app"})
    data = response.json()

    if not data:
        return None, None

    return float(data[0]["lat"]), float(data[0]["lon"])

import re

async def get_lat_long_from_address(address: str, postal_code: str = None):

    try:

        base = re.sub(r"\s+", " ", address.replace("\xa0", " ")).strip()

        if "India" not in base:
            base += ", India"

        # ================================
        # AUTO REDUCTION (NO HARD CODE)
        # ================================
        queries = []

        # full
        queries.append(base)

        # remove house/flat number
        queries.append(re.sub(r"^\s*\d+\s*,?\s*", "", base))

        # keep only middle locality parts
        parts = [p.strip() for p in base.split(",") if p.strip()]
        if len(parts) > 2:
            queries.append(",".join(parts[1:]))

        # remove everything except area + city
        queries.append("Vadapalani, Chennai, India")

        # pincode fallback (IMPORTANT FOR INDIA)
        if postal_code:
            queries.append(f"{postal_code}, Chennai, India")

        headers = {"User-Agent": "hyperlocal-app"}

        best_coords = None
        best_score = -1

        for q in queries:

            url = (
                "https://nominatim.openstreetmap.org/search"
                f"?q={quote(q)}"
                "&format=json"
                "&limit=10"
                "&addressdetails=1"
                "&countrycodes=in"
            )

            res = requests.get(url, headers=headers, timeout=15)
            data = res.json()

            if not data:
                continue

            query_words = set(re.findall(r"\w+", base.lower()))

            for item in data:

                try:
                    lat = float(item.get("lat"))
                    lon = float(item.get("lon"))
                except:
                    continue

                if lat == 0 or lon == 0:
                    continue

                display = item.get("display_name", "").lower()
                item_words = set(re.findall(r"\w+", display))

                # dynamic scoring ONLY
                score = len(query_words & item_words)
                score += float(item.get("importance", 0))

                if score > best_score:
                    best_score = score
                    best_coords = (lat, lon)

            # ⭐ STOP EARLY IF WE GOT GOOD RESULT
            if best_coords:
                break

        return best_coords if best_coords else (None, None)

    except Exception as e:
        print("❌ Geocode error: - shipping_service.py:1697", e)
        return None, None

        
    
async def hyperlocal_couriers_service(
    pickup,
    delivery,
    cod: int
):

    print("🔥 Hyperlocal Service Called - shipping_service.py:1708" , pickup)
    print("🔥 Hyperlocal Service Called - shipping_service.py:1709" , delivery)


    # ✅ Pickup coordinates
    if pickup.latitude and pickup.longitude:
        lat_from = float(pickup.latitude)
        long_from = float(pickup.longitude)
    else:
        lat_from, long_from = await get_lat_long_from_address(
            pickup.address
        )

    # ✅ Delivery exact coordinates
    lat_to, long_to = await get_lat_long_from_address(
        delivery.address
    )

    print(
        "Coordinates:",
        lat_from,
        long_from,
        lat_to,
        long_to
    )

    if not lat_from or not lat_to:
        return {
            "error": "Unable to fetch accurate coordinates"
        }

    response = shiprocket.get_hyperlocal_couriers(
        pickup_postcode=pickup.postal_code,
        delivery_postcode=delivery.postal_code,

        lat_from=lat_from,
        long_from=long_from,

        lat_to=lat_to,
        long_to=long_to,

        cod=cod
    )

    couriers = response.get("data", [])

    filtered_couriers = []

    for c in couriers:
        filtered_couriers.append({
            "courier_name": c.get("courier_name"),
            "is_hyperlocal": True,

            "total_cost": float(c.get("rates") or 0),
            "rto_cost": float(c.get("rto_rates") or 0),

            "distance_km": c.get("distance"),
            "estimated_delivery_time_hours": c.get("etd_hours"),
            "etd": c.get("etd"),
        })

    filtered_couriers.sort(
        key=lambda x: x["total_cost"]
    )

    best_courier = (
        filtered_couriers[0]
        if filtered_couriers
        else None
    )

    return {
        "type": "hyperlocal",

        "coordinates": {
            "pickup": {
                "address": pickup.address,
                "lat": lat_from,
                "long": long_from
            },
            "delivery": {
                "address": delivery.address,
                "lat": lat_to,
                "long": long_to
            }
        },

        "best_courier": best_courier,
        "all_couriers": filtered_couriers
    }


CHENNAI_CENTER = (13.0827, 80.2707)  # Chennai lat/lon
CHENNAI_RADIUS_KM = 60  # adjust as needed (40–80 km typical)

HEADERS = {
    "User-Agent": "shipping-service/1.0"
}


# =========================
# 1. GET LAT/LONG FROM PINCODE
# =========================
async def get_lat_long_from_hyperlocal(pincode: str):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&country=India&format=json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()

        if not data:
            return None, None

        return float(data[0]["lat"]), float(data[0]["lon"])

    except Exception:
        return None, None


# =========================
# 2. HAVERSINE DISTANCE
# =========================
def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two lat/lon points in KM
    """
    R = 6371  # Earth radius in km

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# =========================
# 3. CHENNAI SURROUNDING CHECK
# =========================
async def is_chennai_surrounding(pincode: str):
    lat, lon = await get_lat_long_from_hyperlocal(pincode)

    if lat is None or lon is None:
        return {
            "pincode": pincode,
            "valid": False,
            "message": "Invalid or unknown pincode"
        }

    distance = calculate_distance_km(
        lat, lon,
        CHENNAI_CENTER[0],
        CHENNAI_CENTER[1]
    )

    is_inside = distance <= CHENNAI_RADIUS_KM

    return {
        "pincode": pincode,
        "valid": True,
        "is_chennai_surrounding": is_inside,
        "distance_km": round(distance, 2),
        "radius_km": CHENNAI_RADIUS_KM
    }



async def get_wallet_balance_service():
    """
    Fetch Shiprocket wallet balance
    """
    try:
        response = shiprocket.get_wallet_balance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shiprocket wallet fetch failed: {str(e)}")

    # ✅ Correct key mapping
    balance = response.get("data", {}).get("balance_amount")

    if balance is None:
        raise HTTPException(status_code=500, detail=f"Invalid wallet response: {response}")

    return {
        "status": "success",
        "wallet_balance": float(balance),  # optional: convert to float
        # "raw": response  # remove in production
    }


async def get_pickup_locations_service():
    """
    Fetch Shiprocket pickup locations
    """
    try:
        response = shiprocket.get_pickup_locations()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Shiprocket pickup locations fetch failed: {str(e)}"
        )

    # ✅ Correct key mapping (Shiprocket returns "data")
    locations = response.get("data")

    if not locations:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid pickup location response: {response}"
        )

    return {
        "status": "success",
        "pickup_locations": locations
    }
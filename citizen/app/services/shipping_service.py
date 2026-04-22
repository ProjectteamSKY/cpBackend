from datetime import datetime
import uuid
from fastapi import HTTPException

from app.core.database import execute, query, query_all
from app.utils.query_loader import load_queries
from app.integrations.shiprocket_client import ShiprocketClient

queries = load_queries()
shiprocket = ShiprocketClient()


# ---------------------------------------------------------
# Build Shiprocket Payload
# ---------------------------------------------------------
# def build_shiprocket_payload(order: dict):
#     full_name = order.get("username", "Sriram Pandidurai")
#     names = full_name.strip().split(" ", 1)
#     first_name = names[0]
#     last_name = names[1] if len(names) > 1 else "NA"

#     # ✅ Get valid pickup location from Shiprocket
#     pickup_location_name = "Home"  # <-- replace with your real pickup location


#     return {
#         "order_id": order.get("id"),
#         "order_date": str(order.get("created_at").date()),
#         "pickup_location": pickup_location_name,  # use the valid pickup location

#         # Billing info
#         "billing_customer_name": "Sriram Pandidurai",
#         "billing_first_name": "Sriram",
#         "billing_last_name": "Pandidurai",
#         "billing_address": "35, Indra Nagar, Itteri Road",
#         "billing_city": "Palani",
#         "billing_state": "Tamil Nadu",
#         "billing_country": "India",
#         "billing_pincode": "624601",
#         "billing_email": "crazykidsri@email.com",
#         "billing_phone": "7708012145",

#         # Shipping info (same as billing)
#         "shipping_customer_name": "Sriram Pandidurai",
#         "shipping_first_name": "Sriram",
#         "shipping_last_name": "Pandidurai",
#         "shipping_address": "35, Indra Nagar, Itteri Road",
#         "shipping_city": "Palani",
#         "shipping_state": "Tamil Nadu",
#         "shipping_country": "India",
#         "shipping_pincode": "624601",
#         "shipping_email": "crazykidsri@email.com",
#         "shipping_phone": "7708012145",
#         "shipping_is_billing": True,

#         # Order items
#         "order_items": [
#             {
#                 "name": "CitizenPrints Order",
#                 "sku": "CP-001",
#                 "units": 1,
#                 "selling_price": float(order.get("total_amount", 0))
#             }
#         ],

#         "payment_method": "COD",
#         "sub_total": float(order.get("total_amount", 0)),
#         "length": 10,
#         "breadth": 10,
#         "height": 5,
#         "weight": 0.5
#     }
def build_shiprocket_payload(order: dict, order_items: list):

    # =========================
    # NAME
    # =========================
    first_name = order.get("first_name") or "Customer"
    last_name = order.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip()

    # =========================
    # CLEAN DATA
    # =========================
    state = (order.get("state") or "").replace("\xa0", " ").strip()

    address_line = order.get("address_line") or ""
    city = order.get("city") or ""
    country = order.get("country") or "India"
    postal_code = order.get("postal_code") or ""

    email = order.get("email")
    phone = order.get("phone")

    # =========================
    # ITEMS + WEIGHT
    # =========================
    items_payload = []
    total_weight = 0.0  # ✅ final shipment weight

    for item in order_items:

        product_name = (item.get("product_name") or "").strip()
        units = int(item.get("units") or 1)

        # price handling
        unit_price = float(item.get("unit_price") or 0)
        if unit_price == 0 and item.get("total_price"):
            unit_price = float(item["total_price"]) / units

        # ✅ IMPORTANT: weight is already TOTAL for this item
        item_weight = float(item.get("weight") or 0)

        total_weight += item_weight  # ✅ correct logic

        items_payload.append({
            "name": product_name,
            "sku": product_name.replace(" ", "_")[:40],
            "units": units,
            "selling_price": round(unit_price, 2)
        })

    # =========================
    # FALLBACK (NO ITEMS)
    # =========================
    if not items_payload:
        items_payload = [{
            "name": "Order Item",
            "sku": "CP-001",
            "units": 1,
            "selling_price": float(order.get("total_amount", 0))
        }]
        total_weight = 0.5  # safe fallback

    # =========================
    # SAFETY CHECK
    # =========================
    if total_weight <= 0:
        total_weight = 0.5

    total_weight = round(total_weight, 2)

    # =========================
    # FINAL PAYLOAD
    # =========================
    return {
        "order_id": order.get("id"),
        "order_date": str(order.get("created_at").date()),
        "pickup_location": "Home",

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
        "shipping_customer_name": full_name,
        "shipping_first_name": first_name,
        "shipping_last_name": last_name,
        "shipping_address": address_line,
        "shipping_city": city,
        "shipping_state": state,
        "shipping_country": country,
        "shipping_pincode": postal_code,
        "shipping_email": email,
        "shipping_phone": phone,
        "shipping_is_billing": True,

        # ITEMS
        "order_items": items_payload,

        # PAYMENT
        "payment_method": "COD",
        "sub_total": float(order.get("total_amount", 0)),

        # PACKAGE
        "length": 10,
        "breadth": 10,
        "height": 5,

        # ✅ FINAL CORRECT WEIGHT
        "weight": total_weight
    }
# ---------------------------------------------------------
# Create Shipment
# ---------------------------------------------------------
async def create_order_service(order_id: str):

    order = await query(
        queries["shipping"]["get_order_details"],
        {"id": order_id}
    )
    print("🚀 Order details fetched: - shipping_service.py:200", order)
    if not order:
        raise HTTPException(404, "Order not found")
    
    order_items = await query_all(
        queries["order_item"]["get_all_order_item"],
        {"order_id": order_id}
    )

    print("🛒 Order items fetched: - shipping_service.py:209", order_items)

    
    payload = build_shiprocket_payload(order , order_items)
    print("🚀 Built Shiprocket Payload: - shipping_service.py:213", payload)
    try:
        print("🚀 PAYLOAD: - shipping_service.py:215", payload)
        response = shiprocket.create_order(payload)
        print("✅ SHIPROCKET RESPONSE: - shipping_service.py:217", response)
    except Exception as e:
        print("❌ SHIPROCKET ERROR: - shipping_service.py:219", str(e))
        raise HTTPException(500, f"Shiprocket API call failed: {str(e)}")

    shipment_id = response.get("shipment_id")

    if not shipment_id:
        raise HTTPException(
            500,
            f"Shiprocket did not return shipment_id. Response: {response}"
        )

    # ✅ FIX HERE
    awb_code = response.get("awb_code") or None
    courier_name = response.get("courier_name") or None

    shipment_uuid = str(uuid.uuid4())

    await execute(
        queries["shipping"]["create_shipment"],
        {
            "id": shipment_uuid,
            "order_id": order_id,
            "shiprocket_order_id": response.get("order_id"),
            "shipment_id": shipment_id,
            "awb_code": awb_code,          # ✅ now NULL instead of ''
            "courier_name": courier_name,  # ✅ now NULL instead of ''
            "tracking_url": None,
            "current_status": response.get("status"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    )

    return {
        "status": "success",
        "shipment_id": shipment_id,
        "shiprocket_order_id": response.get("order_id"),
        "awb_code": awb_code,
        "courier_name": courier_name
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

    # ✅ Prevent duplicate assignment
    if shipment.get("awb_code"):
        return {
            "status": "success",
            "message": "Courier already assigned",
            "awb_code": shipment.get("awb_code"),
            "courier_name": shipment.get("courier_name")
        }

    # ---------------------------------------------------------
    # ✅ Get courier list
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
    # ✅ Find best courier
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

    # ---------------------------------------------------------
    # ✅ Assign courier (AWB)
    # ---------------------------------------------------------
    assign_response = shiprocket.assign_courier(
        shipment_id,
        best_courier["courier_id"]
    )

    if not assign_response:
        raise HTTPException(500, "Courier assignment failed")

    freight_charges = float(assign_response.get("freight_charges") or 0)

    # ---------------------------------------------------------
    # ✅ Save shipment data
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
    # ✅ UPDATE ORDER STATUS → shipment
    # ---------------------------------------------------------
    await execute(
        queries["orders"]["update_order_status"],
        {
            "order_id": order_id,
            "status": "shipment"
        }
    )

    # ---------------------------------------------------------
    # ✅ ADD FREIGHT TO TOTAL PRICE
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


# ---------------------------------------------------------
# Webhook Status Update
# ---------------------------------------------------------
async def update_webhook_status_service(payload: dict):

    awb_code = payload.get("awb")

    order_status = (
        payload.get("current_status")
        or payload.get("shipment_status")
        or payload.get("status")
    )

    if not awb_code or not order_status:
        raise HTTPException(400, "Invalid webhook payload")

    status_map = {
        "picked up": "shipped",
        "in transit": "shipped",
        "out for delivery": "shipped",
        "delivered": "delivered",
        "delivered to consignee": "delivered",
        "cancelled": "cancelled",
        "rto initiated": "rto"
    }

    status_clean = order_status.strip().lower()
    final_status = status_map.get(status_clean, status_clean)

    delivered_at = datetime.utcnow() if final_status == "delivered" else None

    await execute(
        queries["shipping"]["update_status"],
        {
            "status": final_status,
            "awb_code": awb_code
        }
    )

    await execute(
        queries["shipping"]["update_order_status"],
        {
            "status": final_status,
            "awb_code": awb_code
        }
    )

    return {
        "status": "success",
        "message": f"Webhook processed: {final_status}"
    }


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

    response = shiprocket.cancel_order(shipment["shiprocket_order_id"])

    await execute(
        queries["shipping"]["cancel_order"],
        {"order_id": order_id}
    )

    return {
        "status": "success",
        "message": "Order cancelled",
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




async def couriers_service(
    pickup_postcode: str,
    delivery_postcode: str,
    weight: float,
    cod: int,
    declared_value: float
):
    """
    Fetch couriers from Shiprocket API and return:
    1. Full filtered courier list
    2. Single best courier based on lowest total cost
    """
    print("API triggers for courier availability - shipping_service.py:596")
    
    # Call Shiprocket API
    response = shiprocket.get_couriers_by_address(
        pickup_postcode=pickup_postcode,
        delivery_postcode=delivery_postcode,
        weight=weight,
        cod=cod,
        declared_value=declared_value
    )
    
    couriers = response.get("data", {}).get("available_courier_companies", [])
    
    # Filter required fields
    filtered_couriers = []
    for c in couriers:
        filtered_couriers.append({
            "courier_name": c.get("courier_name"),
            "courier_type": "Surface" if c.get("is_surface") else "Air",
            "city": c.get("city"),
            "state": c.get("state"),
            "postcode": c.get("postcode"),
            "rate": c.get("rate") or 0,                      # base rate
            "freight_charge": c.get("freight_charge") or 0,  # final charge
            "other_charges": c.get("other_charges") or 0,    # additional charges
            "cod": c.get("cod"),
            "cod_charges": c.get("cod_charges") or 0,
            "total_cost": (c.get("freight_charge") or 0) + (c.get("other_charges") or 0) + ((c.get("cod_charges") or 0) if cod else 0),
            "estimated_delivery_days": c.get("estimated_delivery_days"),
            "etd": c.get("etd"),
            "pickup_availability": c.get("pickup_availability"),
            "delivery_performance": c.get("delivery_performance"),
            "pickup_performance": c.get("pickup_performance"),
            "rating": c.get("rating"),
            "surface_max_weight": c.get("surface_max_weight"),
            "air_max_weight": c.get("air_max_weight")
        })
    
    # Sort by total cost (lowest first)
    filtered_couriers.sort(key=lambda x: x["total_cost"])
    
    # Best single courier (lowest total cost)
    best_courier = filtered_couriers[0] if filtered_couriers else None
    
    return {
        "best_courier": best_courier
    }

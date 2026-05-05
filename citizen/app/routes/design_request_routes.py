from typing import Optional, List
import json
import uuid

from fastapi import APIRouter, Body, HTTPException, UploadFile, File, Form
from app.core.database import execute, query, query_all

from app.services.design_request_service import (
    create_design_request,
    get_all_design_requests,
    get_design_request_by_id,
    update_design_request,
    delete_design_request,
    get_design_requests_by_user_id
)
from app.utils.image_compresser import upload_images
from app.domain.cart_domain import Cart
from app.services.cart_item_service import create_cart_item
from app.services.cart_service import create_cart, get_cart_by_user_id
from app.utils.query_loader import load_queries
from app.services.variant_price_service import get_variant_price_by_id
from datetime import datetime, timezone
router = APIRouter()
queries = load_queries()

LOGO_UPLOAD_FOLDER = "media/designrequestlogo"
DESIGN_UPLOAD_FOLDER = "media/designedimages"


# Helper: parse JSON string fields into lists
def parse_images(item: dict):
    item["logo_images"] = json.loads(item.get("logo_images") or "[]")
    item["designed_images"] = json.loads(item.get("designed_images") or "[]")
    return item

def get_print_location(selected_attributes):
    try:
        attrs = json.loads(selected_attributes or "[]")
    except:
        return None

    for attr in attrs:
        if attr.get("attribute_name") == "print location":
            return attr.get("attribute_value_name")

    return None
# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_design_request_endpoint(
    user_id: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    email: Optional[str] = Form(None),

    product_id: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),

    variant_id: Optional[str] = Form(None),
    variant_price_id: Optional[str] = Form(None),

    selected_attributes: Optional[str] = Form("{}"),

    design_notes: Optional[str] = Form(None),
    design_price: Optional[float] = Form(None),

    logo_files: List[UploadFile] = File([])
):
    logo_images = upload_images(logo_files, LOGO_UPLOAD_FOLDER)

    data = {
    "id": str(uuid.uuid4()),

    "user_id": user_id,
    "name": name,
    "phone": phone,
    "email": email,

    "product_id": product_id,
    "product_name": product_name,

    "variant_id": variant_id,
    "variant_price_id": variant_price_id,

    "selected_attributes": selected_attributes,
    "design_notes": design_notes,
    "design_price": design_price or 0.0,

    "logo_images": json.dumps(logo_images),
    "designed_images": json.dumps([]),

    # 🔥 REQUIRED FIXES
    "revision_count": 0,
    "rejection_reason": None,

    "status": "NEW",
    "is_approved": False,

    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc),
}

    await execute(queries["design_request"]["create"], data)

    return await get_design_request_by_id(data["id"])

# --------------------------
# UPDATE (LOGO + DESIGNED IMAGES + Other Fields)
# --------------------------
@router.post("/{id}/update")
async def update_design_request_endpoint(
    id: str,

    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),

    product_id: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),

    variant_id: Optional[str] = Form(None),
    product_variant_price_id: Optional[str] = Form(None),

    selected_attributes: Optional[str] = Form(None),
    design_notes: Optional[str] = Form(None),
    design_price: Optional[float] = Form(None),

    logo_files: List[UploadFile] = File([]),
    designed_files: List[UploadFile] = File([])
):

    # 1️⃣ Fetch existing request
    existing = await get_design_request_by_id(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Design request not found")

    # 2️⃣ SAFE PARSE logo_images
    try:
        old_logos = json.loads(existing.get("logo_images") or "[]")
        if not isinstance(old_logos, list):
            old_logos = []
    except:
        old_logos = []

    # 3️⃣ SAFE PARSE designed_images (versioned)
    try:
        old_designs = json.loads(existing.get("designed_images") or "[]")
        if not isinstance(old_designs, list):
            old_designs = []
    except:
        old_designs = []

    # 4️⃣ Parse selected attributes (IMPORTANT FIX)
    try:
        parsed_attributes = json.loads(selected_attributes) if selected_attributes else json.loads(existing.get("selected_attributes") or "[]")
    except:
        parsed_attributes = []

    # ----------------------------
    # PRINT LOCATION RULE (same as approve)
    # ----------------------------
    print_location = None
    for attr in parsed_attributes:
        if attr.get("attribute_name") == "print location":
            print_location = attr.get("attribute_value_name")
            break

    # 5️⃣ Upload new files
    new_logos = upload_images(logo_files, LOGO_UPLOAD_FOLDER) if logo_files else []
    new_designs = upload_images(designed_files, DESIGN_UPLOAD_FOLDER) if designed_files else []

    # 6️⃣ Merge logos (no versioning)
    logo_images = old_logos + new_logos

    # 7️⃣ Versioning for designs
    if old_designs and isinstance(old_designs[-1], dict) and "version" in old_designs[-1]:
        next_version = old_designs[-1]["version"] + 1
    else:
        next_version = 1

    if new_designs:
        old_designs.append({
            "version": next_version,
            "status": "PENDING",
            "images": new_designs,
            "created_at": datetime.utcnow().isoformat()
        })

    # ----------------------------
    # VALIDATION (same as approve)
    # ----------------------------
    latest_version = old_designs[-1] if old_designs else None
    latest_images = latest_version.get("images", []) if isinstance(latest_version, dict) else []

    if print_location == "back" and len(latest_images) < 2:
        raise HTTPException(
            status_code=400,
            detail="Back print requires 2 design images (front + back)"
        )

    # ----------------------------
    # FRONT / BACK MAPPING (stored consistency)
    # ----------------------------
    front = latest_images[0] if len(latest_images) > 0 else None
    back = latest_images[1] if len(latest_images) > 1 else None

    update_data = {
        "name": name or existing.get("name"),
        "phone": phone or existing.get("phone"),
        "email": email or existing.get("email"),

        "product_id": product_id or existing.get("product_id"),
        "product_name": product_name or existing.get("product_name"),

        "variant_id": variant_id or existing.get("variant_id"),
        "product_variant_price_id": product_variant_price_id or existing.get("product_variant_price_id"),

        "selected_attributes": json.dumps(parsed_attributes),
        "design_notes": design_notes or existing.get("design_notes"),
        "design_price": design_price if design_price is not None else existing.get("design_price"),

        "logo_images": json.dumps(logo_images),
        "designed_images": json.dumps(old_designs),

        # optional but useful for frontend consistency
        "latest_front_image": front,
        "latest_back_image": back
    }

    # 8️⃣ UPDATE DB
    updated = await update_design_request(id, update_data)

    return {
        "status": "success",
        "message": "Design request updated successfully",
        "data": parse_images(updated)
    }

# --------------------------
# UPDATE STATUS
# --------------------------
@router.post("/{id}/status")
async def update_design_status(
    id: str,
    payload: dict = Body(...)
):
    status = payload.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")

    valid_status = ["NEW", "IN_PROGRESS", "DESIGN_COMPLETED", "REJECTED", "APPROVED"]
    if status not in valid_status:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {valid_status}")

    updated = await update_design_request(id, {"status": status})
    if not updated:
        raise HTTPException(status_code=404, detail="Design request not found")

    return {
        "status": "success",
        "message": f"Status updated to {status}",
        "data": parse_images(updated)
    }


# --------------------------
# APPROVE / REJECT
# --------------------------
@router.put("/designedimage/{id}/approve")
async def approve_design(id: str):

    # =====================================================
    # FETCH DESIGN
    # =====================================================
    design = await get_design_request_by_id(id)

    print("Fetched design request: - design_request_routes.py:278", design)

    if not design:
        raise HTTPException(status_code=404, detail="Design request not found")

    price_id = design.get("variant_price_id")
    if not price_id:
        raise HTTPException(status_code=400, detail="Missing variant_price_id")

    # =====================================================
    # FETCH PRICE ROW
    # =====================================================
    price_row = await get_variant_price_by_id(price_id)

    print("Fetched price row: - design_request_routes.py:292", price_row)

    if not price_row:
        raise HTTPException(status_code=400, detail="Invalid price ID")

    if not price_row.get("is_active"):
        raise HTTPException(status_code=400, detail="Price is inactive")

    # =====================================================
    # PRICE DETAILS
    # =====================================================
    min_qty = int(price_row["min_qty"])
    max_qty = int(price_row["max_qty"]) if price_row.get("max_qty") else None
    unit_price = float(price_row["price"])

    # =====================================================
    # ✅ FIXED: USE MAX QTY ONLY
    # =====================================================
    if max_qty:
        quantity = max_qty
    else:
        quantity = min_qty  # fallback safety

    # =====================================================
    # CART
    # =====================================================
    user_id = design["user_id"]

    cart = await get_cart_by_user_id(user_id)
    if not cart:
        cart = await create_cart(Cart(user_id=user_id))

    cart_id = cart["id"]

    # =====================================================
    # ✅ KEEP ORIGINAL ATTRIBUTE FORMAT (LIST)
    # =====================================================
    try:
        selected_attributes = json.loads(design.get("selected_attributes") or "[]")
    except:
        selected_attributes = []

    # =====================================================
    # IMAGES
    # =====================================================
    images_raw = design.get("designed_images") or []

    if isinstance(images_raw, str):
        try:
            images_raw = json.loads(images_raw)
        except:
            images_raw = []

    latest_images = []
    if isinstance(images_raw, list) and images_raw:
        latest_images = (images_raw[-1] or {}).get("images", [])

    latest_images = [i.replace("\\", "/") for i in latest_images]

    # detect print location from attributes
    print_location = None
    for attr in selected_attributes:
        if attr.get("attribute_name") == "print location":
            print_location = attr.get("attribute_value_name")

    if print_location == "back" and len(latest_images) < 2:
        raise HTTPException(status_code=400, detail="Back print requires 2 images")

    front = latest_images[0] if len(latest_images) > 0 else None
    back = latest_images[1] if len(latest_images) > 1 else None

    # =====================================================
    # PAYLOAD
    # =====================================================
    class Payload:
        pass

    payload = Payload()
    payload.cart_id = cart_id
    payload.product_id = design["product_id"]
    payload.variant_id = design["variant_id"]
    payload.variant_price_id = price_id
    payload.quantity = quantity
    payload.selected_attributes = selected_attributes  # ✅ FIXED

    # =====================================================
    # CREATE CART ITEM
    # =====================================================
    try:
        cart_item = await create_cart_item(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # =====================================================
    # INSERT CART FILES
    # =====================================================
    if cart_item and "id" in cart_item:
        await execute(
            queries["cart_items"]["insert_cart_files"],
            {
                "id": str(uuid.uuid4()),
                "cart_item_id": cart_item["id"],
                "front_side_url": front,
                "back_side_url": back,
                "front_original_name": "design_front",
                "back_original_name": "design_back",
            }
        )

    # =====================================================
    # UPDATE DESIGN STATUS
    # =====================================================
    await update_design_request(
        id,
        {"is_approved": True, "status": "APPROVED"}
    )

    # =====================================================
    # RESPONSE
    # =====================================================
    return {
        "status": "success",
        "message": "Design approved & added to cart",
        "data": {
            "quantity": quantity,
            "unit_price": unit_price,
            "total": quantity * unit_price,
            "min_qty": min_qty,
            "max_qty": max_qty
        }
    }

@router.put("/designedimage/{id}/reject")
async def reject_design(
    id: str,
    rejection_reason: Optional[str] = Form(None)
):
    design = await get_design_request_by_id(id)
    if not design:
        raise HTTPException(status_code=404, detail="Design request not found")

    # 1️⃣ Parse versions safely
    try:
        designs = json.loads(design.get("designed_images") or "[]")
    except:
        designs = []

    if not designs:
        raise HTTPException(status_code=400, detail="No design versions found")

    # 2️⃣ Update latest version
    latest = designs[-1]
    latest["status"] = "REJECTED"
    latest["rejection_reason"] = rejection_reason or ""

    # 3️⃣ Decide GLOBAL status correctly
    global_status = "REJECTED"

    # 4️⃣ Save
    updated = await update_design_request(id, {
        "designed_images": json.dumps(designs),
        "status": global_status,
        "is_approved": False,
        "revision_count": (design.get("revision_count") or 0) + 1
    })

    return {
        "status": "success",
        "message": "Design rejected",
        "data": parse_images(updated)
    }
# --------------------------
# GET LIST / GET BY ID / GET BY USER
# --------------------------
@router.get("/list")
async def list_design_requests():
    data = await get_all_design_requests()
    data = [parse_images(d) for d in data]
    return {"status": "success", "data": data}


@router.get("/{id}")
async def get_design_request_endpoint(id: str):
    data = await get_design_request_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "success", "data": parse_images(data)}


@router.get("/user/{user_id}")
async def get_design_requests_by_user(user_id: str):
    data = await get_design_requests_by_user_id(user_id)
    data = [parse_images(d) for d in data]
    return {"status": "success", "data": data}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_design_request_endpoint(id: str):
    deleted = await delete_design_request(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return {"status": "success", "deleted_id": id}
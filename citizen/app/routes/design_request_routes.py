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
from app.services.product_variant_price_service import get_product_variant_price_by_id

router = APIRouter()
queries = load_queries()

LOGO_UPLOAD_FOLDER = "media/designrequestlogo"
DESIGN_UPLOAD_FOLDER = "media/designedimages"


# Helper: parse JSON string fields into lists
def parse_images(item: dict):
    item["logo_images"] = json.loads(item.get("logo_images") or "[]")
    item["designed_images"] = json.loads(item.get("designed_images") or "[]")
    return item


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
        "designed_images": json.dumps([])
    }

    created = await create_design_request(data)
    return {"status": "success", "data": parse_images(created)}


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
    design_notes: Optional[str] = Form(None),
    design_price: Optional[float] = Form(None),
    logo_files: List[UploadFile] = File([]),
    designed_files: List[UploadFile] = File([])
):
    # Fetch existing request
    existing = await get_design_request_by_id(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Design request not found")

    # Merge logo images
    old_logos = json.loads(existing.get("logo_images") or "[]")
    new_logos = upload_images(logo_files, LOGO_UPLOAD_FOLDER) if logo_files else []
    logo_images = old_logos + new_logos

    # Merge designed images
    old_designs = json.loads(existing.get("designed_images") or "[]")
    new_designs = upload_images(designed_files, DESIGN_UPLOAD_FOLDER) if designed_files else []
    designed_images = old_designs + new_designs

    # Prepare update payload
    update_data = {
        "name": name or existing.get("name"),
        "phone": phone or existing.get("phone"),
        "email": email or existing.get("email"),
        "product_id": product_id or existing.get("product_id"),
        "product_name": product_name or existing.get("product_name"),
        "variant_id": variant_id or existing.get("variant_id"),
        "variant_price_id": variant_price_id or existing.get("variant_price_id"),
        "selected_attributes": selected_attributes or existing.get("selected_attributes"),
        "design_notes": design_notes or existing.get("design_notes"),
        "design_price": design_price if design_price is not None else existing.get("design_price"),
        "logo_images": json.dumps(logo_images),
        "designed_images": json.dumps(designed_images)
    }

    updated = await update_design_request(id, update_data)
    return {"status": "success", "data": parse_images(updated)}


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

    # 1️⃣ Get design request
    design = await get_design_request_by_id(id)
    if not design:
        raise HTTPException(status_code=404, detail="Design request not found")

    # 2️⃣ Validate required fields
    price_id = design.get("product_variant_price_id")
    if not price_id:
        raise HTTPException(status_code=400, detail="Missing product_variant_price_id")

    if not design.get("product_id") or not design.get("variant_id"):
        raise HTTPException(status_code=400, detail="Product or variant missing")

    user_id = design["user_id"]

    # 3️⃣ Get price
    price_row = await get_product_variant_price_by_id(price_id)

    if not price_row:
        raise HTTPException(status_code=400, detail="Invalid price ID")

    if not price_row.get("is_active"):
        raise HTTPException(status_code=400, detail="Price is inactive")

    quantity = price_row["min_qty"]
    unit_price = price_row["price"]

    # 4️⃣ Get or create cart
    cart = await get_cart_by_user_id(user_id)
    if not cart:
        cart = await create_cart(Cart(user_id=user_id))

    cart_id = cart["id"]

    # 5️⃣ Update design status
    await update_design_request(
        id,
        {"is_approved": True, "status": "APPROVED"}
    )

    # 6️⃣ Prepare payload
    # 6️⃣ Prepare payload
    class Payload:
        pass

    payload = Payload()
    payload.cart_id = cart_id
    payload.product_id = design["product_id"]
    payload.variant_id = design["variant_id"]
    payload.quantity = quantity
    payload.product_variant_price_id = price_id
    payload.customize_qty = quantity

    # ✅ FIXED LINE
    payload.selected_options = json.loads(design.get("selected_attributes") or "{}")

    payload.front_file = None
    payload.back_file = None

    # 7️⃣ Create cart item
    try:
        cart_item = await create_cart_item(payload)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Cart item creation failed: {str(e)}"
        )

    # 8️⃣ Handle designed images (🔥 FIXED FULLY)
    images_raw = design.get("designed_images") or []

    # Convert to list if needed
    if isinstance(images_raw, str):
        try:
            images = json.loads(images_raw)
        except Exception:
            images = []
    elif isinstance(images_raw, list):
        images = images_raw
    else:
        images = []

    # Extract front/back safely
    front = None
    back = None

    if len(images) == 1:
        front = images[0]
    elif len(images) >= 2:
        front = images[0]
        back = images[1]

    # Normalize file paths (Windows → URL safe)
    if front:
        front = front.replace("\\", "/")
    if back:
        back = back.replace("\\", "/")

    # Debug (optional)
    print("FINAL FRONT: - design_request_routes.py:272", front)
    print("FINAL BACK: - design_request_routes.py:273", back)

    # 9️⃣ Insert cart item files
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

    # 🔟 Final response
    return {
        "status": "success",
        "message": "Design approved & added to cart",
        "data": {
            "quantity": quantity,
            "unit_price": unit_price,
            "total": quantity * unit_price,
            "cart_item": cart_item,
            "images_used": {
                "front": front,
                "back": back
            }
        }
    }


@router.put("/designedimage/{id}/reject")
async def reject_design(id: str):
    updated = await update_design_request(id, {"is_approved": False, "status": "REJECTED"})
    if not updated:
        raise HTTPException(status_code=404, detail="Design request not found")
    return {"status": "success", "message": "Design rejected", "data": parse_images(updated)}

    
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
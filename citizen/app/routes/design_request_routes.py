# app/routes/design_request_routes.py

from typing import Optional, List
import json

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.services.design_request_service import (
    create_design_request,
    get_all_design_requests,
    get_design_request_by_id,
    update_design_request,
    delete_design_request,
    get_design_requests_by_user_id
)
from app.utils.image_compresser import upload_images

router = APIRouter()

LOGO_UPLOAD_FOLDER = "media/designrequestlogo"
DESIGN_UPLOAD_FOLDER = "media/designedimages"


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

    # ✅ NEW
    variant_id: Optional[str] = Form(None),
    product_variant_price_id: Optional[str] = Form(None),

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

        # ✅ NEW
        "variant_id": variant_id,
        "product_variant_price_id": product_variant_price_id,

        "design_notes": design_notes,
        "logo_images": json.dumps(logo_images),
        "designed_images": json.dumps([]),
        "design_price": design_price or 0.0
    }

    created = await create_design_request(data)

    return {"status": "success", "data": created}


# --------------------------
# UPLOAD DESIGNED IMAGES
# --------------------------
@router.post("/{id}/upload-designs")
async def upload_designed_images(
    id: str,
    files: List[UploadFile] = File(...)
):
    images = upload_images(files, DESIGN_UPLOAD_FOLDER)

    updated = await update_design_request(id, {
        "designed_images": json.dumps(images),
        "status": "DESIGNED"
    })

    if not updated:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "data": updated}


# --------------------------
# APPROVE
# --------------------------
@router.put("/{id}/approve")
async def approve_design(id: str):
    updated = await update_design_request(id, {
        "is_approved": True,
        "status": "APPROVED"
    })

    if not updated:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "data": updated}


# --------------------------
# REJECT
# --------------------------
@router.put("/{id}/reject")
async def reject_design(id: str):
    updated = await update_design_request(id, {
        "is_approved": False,
        "status": "REJECTED"
    })

    if not updated:
        raise HTTPException(status_code=404, detail="Not found")

    return {"status": "success", "data": updated}


# --------------------------
# LIST
# --------------------------
@router.get("/list")
async def list_design_requests():
    data = await get_all_design_requests()

    for item in data:
        item["logo_images"] = json.loads(item.get("logo_images") or "[]")
        item["designed_images"] = json.loads(item.get("designed_images") or "[]")

    return {"status": "success", "data": data}


# --------------------------
# GET BY ID
# --------------------------
@router.get("/{id}")
async def get_design_request_endpoint(id: str):
    data = await get_design_request_by_id(id)

    if not data:
        raise HTTPException(status_code=404, detail="Not found")

    data["logo_images"] = json.loads(data.get("logo_images") or "[]")
    data["designed_images"] = json.loads(data.get("designed_images") or "[]")

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


@router.get("/user/{user_id}")
async def get_design_requests_by_user(user_id: str):
    data = await get_design_requests_by_user_id(user_id)

    # ✅ parse JSON fields
    for item in data:
        item["logo_images"] = json.loads(item.get("logo_images") or "[]")
        item["designed_images"] = json.loads(item.get("designed_images") or "[]")

    return {"status": "success", "data": data}
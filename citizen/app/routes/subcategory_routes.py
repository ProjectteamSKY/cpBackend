import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image   # ✅ FIXED

from app.domain.subcategory_domain import Subcategory
from app.services.subcategory_service import (
    create_subcategory,
    get_all_subcategories,
    get_subcategory_by_id,
    get_subcategories_by_category,
    update_subcategory,
    delete_subcategory,
    activate_subcategory,
    deactivate_subcategory
)

router = APIRouter()

# ----------------------------
# CONFIG
# ----------------------------
UPLOAD_FOLDER = "media/subcategory"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_TYPES = ["image/jpeg", "image/png"]


# ----------------------------
# IMAGE PROCESSING
# ----------------------------

def process_and_save_image(file: UploadFile) -> dict:
    """
    Validate, compress and save image
    """

    # ✅ validate type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Invalid file type: {file.content_type}")

    try:
        image = Image.open(file.file)
    except Exception:
        raise HTTPException(400, "Invalid image file")

    # ✅ convert to RGB
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # ✅ resize
    image.thumbnail((800, 800))

    # ✅ filename
    filename = f"{uuid.uuid4()}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)

    # ✅ compress & save
    image.save(
        path,
        format="JPEG",
        quality=70,
        optimize=True
    )

    return {
        "id": str(uuid.uuid4()),
        "url": path.replace("\\", "/"),
        "is_default": False
    }


def upload_images(files: List[UploadFile]) -> List[dict]:
    """
    Handle multiple images
    """

    images = []

    for index, file in enumerate(files):
        img = process_and_save_image(file)

        # ✅ first image default
        if index == 0:
            img["is_default"] = True

        images.append(img)

    return images


# ----------------------------
# CREATE
# ----------------------------

@router.post("/create")
async def create_subcategory_endpoint(
    category_id: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    is_active: bool = Form(True),
    images: Optional[List[UploadFile]] = File(None),
):

    images_list = upload_images(images) if images else []

    subcategory = Subcategory(
        category_id=category_id,
        name=name,
        description=description,
        images=images_list,
        is_active=is_active
    )

    return await create_subcategory(subcategory)


# ----------------------------
# LIST
# ----------------------------

@router.get("/list")
async def list_subcategories(category_id: Optional[str] = None):

    if category_id:
        data = await get_subcategories_by_category(category_id)
    else:
        data = await get_all_subcategories()

    return {"subcategories": data}


# ----------------------------
# GET BY ID
# ----------------------------

@router.get("/{id}")
async def get_subcategory_endpoint(id: str):

    data = await get_subcategory_by_id(id)

    if not data:
        raise HTTPException(404, "Subcategory not found")

    return data


# ----------------------------
# UPDATE
# ----------------------------

@router.put("/update/{id}")
async def update_subcategory_endpoint(
    id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
):

    payload = {}

    if name is not None:
        payload["name"] = name

    if description is not None:
        payload["description"] = description

    if is_active is not None:
        payload["is_active"] = is_active

    # ✅ images update
    if images:
        payload["images"] = upload_images(images)

    if not payload:
        raise HTTPException(400, "No fields to update")

    result = await update_subcategory(id, payload)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return {
        "status": "success",
        "data": result
    }


# ----------------------------
# DELETE
# ----------------------------

@router.delete("/delete/subcategory/{id}")
async def delete_subcategory_endpoint(id: str):

    result = await delete_subcategory(id)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return {
        "status": "success",
        "deleted_id": id
    }


# ----------------------------
# ACTIVATE
# ----------------------------

@router.put("/{id}/activate")
async def activate_subcategory_endpoint(id: str):

    result = await activate_subcategory(id)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return result


# ----------------------------
# DEACTIVATE
# ----------------------------

@router.put("/{id}/deactivate")
async def deactivate_subcategory_endpoint(id: str):

    result = await deactivate_subcategory(id)

    if not result:
        raise HTTPException(404, "Subcategory not found")

    return result
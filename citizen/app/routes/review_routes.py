import os
import uuid
import shutil
from typing import Optional, List

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.domain.review_domain import CustomerReview
from app.services.review_service import (
    create_review,
    get_all_reviews,
    get_review_by_id,
    update_review,
    delete_review,
    activate_review,
    deactivate_review,
    latest_reviews
)

router = APIRouter()

# --------------------------
# File Upload Config
# --------------------------
UPLOAD_FOLDER = "media/reviews"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file: UploadFile) -> str:
    """Save an uploaded file and return its relative path."""
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return path.replace("\\", "/")  # For Windows compatibility

# --------------------------
# Pydantic Models
# --------------------------
class ReviewCreate(BaseModel):
    product_id: str
    user_id: str
    customer_name: str
    rating: float
    comment: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

# --------------------------
# CREATE Review
# --------------------------
@router.post("/create")
async def create_review_endpoint(
    product_id: str = Form(...),
    user_id: str = Form(...),
    rating: float = Form(...),
    comment: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None)
):
    review_data = {
        "product_id": product_id,
        "user_id": user_id,
        "rating": rating,
        "comment": comment,
        "is_active": is_active
    }

    if image:
        review_data["image_url"] = save_upload(image)

    review = CustomerReview(**review_data)
    created = await create_review(review)
    return {"status": "success", "data": created}
# --------------------------
# UPDATE Review
# --------------------------
@router.put("/{id}")
async def update_review_endpoint(id: str, payload: ReviewUpdate, image: Optional[UploadFile] = File(None)):
    updates = payload.model_dump(exclude_unset=True)
    if image:
        updates["image_url"] = save_upload(image)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await update_review(id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "data": updated}

# --------------------------
# LIST / GET / DELETE / ACTIVATE / DEACTIVATE
# --------------------------
@router.get("/list")
async def list_reviews():
    reviews = await get_all_reviews()
    return {"status": "success", "reviews": reviews}

@router.get("/{id}")
async def get_review_endpoint(id: str):
    review = await get_review_by_id(id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "data": review}

@router.delete("/{id}")
async def delete_review_endpoint(id: str):
    result = await delete_review(id)
    if not result:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "deleted_id": id}

@router.put("/{id}/activate")
async def activate_review_endpoint(id: str):
    result = await activate_review(id)
    if not result:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "data": result}

@router.put("/{id}/deactivate")
async def deactivate_review_endpoint(id: str):
    result = await deactivate_review(id)
    if not result:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "data": result}

# --------------------------
# LATEST 5 Reviews per Product
# --------------------------
@router.get("/product/{product_id}/latest")
async def latest_reviews_endpoint(product_id: str):
    reviews = await latest_reviews(product_id)
    return {"status": "success", "reviews": reviews}
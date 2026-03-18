import os
import shutil
import uuid

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.domain.product_discount_domain import ProductDiscount
from app.services.product_discount_service import (
    create_product_discount,
    get_all_product_discounts,
    get_all_product_discounts_active,
    get_product_discount_by_id,
    get_product_discounts_by_product,
    update_product_discount,
    delete_product_discount,
    activate_product_discount,
    deactivate_product_discount,
    get_product_discounts_by_date_range,
    get_last5_active_product_discounts
)

router = APIRouter()

# ---------------- Pydantic Models ----------------
class ProductDiscountCreate(BaseModel):
    product_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    discount: str = "0%"
    banner_image_url: Optional[str]
    cta_text: Optional[str]
    start_date: datetime
    end_date: datetime

class ProductDiscountUpdate(BaseModel):
    product_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    discount: Optional[str] = None
    banner_image_url: Optional[str] = None
    cta_text: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

UPLOAD_FOLDER = "media/bannerimages"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file: UploadFile) -> str:
    """
    Save uploaded file to UPLOAD_FOLDER and return the relative path.
    """
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # return path with forward slashes for consistency
    return path.replace("\\", "/")

# ---------------- CREATE ----------------
@router.post("/create")
async def create_product_discount_endpoint(
    product_id: str = Form(None),
    title: str = Form(...),
    description: str = Form(None),
    discount: str = Form("0%"),
    banner_file: UploadFile = None,
    cta_text: str = Form(None),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    # convert dates
    parsed_start = datetime.fromisoformat(start_date)
    parsed_end = datetime.fromisoformat(end_date)
    if parsed_start > parsed_end:
        raise HTTPException(400, "start_date cannot be after end_date")
    
    # save banner image if uploaded
    banner_image_url = save_upload(banner_file) if banner_file else None
    
    # create domain object
    pd = ProductDiscount(
        product_id=product_id,
        title=title,
        description=description,
        discount=discount,
        banner_image_url=banner_image_url,
        cta_text=cta_text,
        start_date=parsed_start,
        end_date=parsed_end
    )
    
    return await create_product_discount(pd)

# ---------------- GET ALL ----------------
@router.get("/list")
async def list_product_discounts():
    return {"discounts": await get_all_product_discounts()}

@router.get("/list/active")
async def list_product_discounts_active():
    return {"discounts": await get_all_product_discounts_active()}

# ---------------- GET BY ID ----------------
@router.get("/{id}")
async def get_product_discount_endpoint(id: str):
    discount = await get_product_discount_by_id(id)
    if not discount:
        raise HTTPException(404, "Product Discount not found")
    return discount

# ---------------- GET BY PRODUCT ----------------
@router.get("/product/{product_id}")
async def list_product_discounts_by_product(product_id: str):
    return {"discounts": await get_product_discounts_by_product(product_id)}

# ---------------- UPDATE ----------------
@router.put("/{id}")
async def update_product_discount_endpoint(
    id: str,
    product_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    discount: Optional[str] = Form(None),
    banner_image_url: Optional[str] = Form(None),
    cta_text: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
):
    existing = await get_product_discount_by_id(id)
    if not existing:
        raise HTTPException(404, "Product Discount not found")

    parsed_start = datetime.fromisoformat(start_date) if start_date else existing["start_date"]
    parsed_end = datetime.fromisoformat(end_date) if end_date else existing["end_date"]

    if parsed_start > parsed_end:
        raise HTTPException(400, "start_date cannot be after end_date")

    pd = ProductDiscount(
        product_id=product_id or existing["product_id"],
        title=title or existing.get("title"),
        description=description or existing.get("description"),
        discount=discount or existing.get("discount"),
        banner_image_url=banner_image_url or existing.get("banner_image_url"),
        cta_text=cta_text or existing.get("cta_text"),
        start_date=parsed_start,
        end_date=parsed_end,
    )

    return await update_product_discount(id, pd)

# ---------------- SOFT DELETE ----------------
@router.delete("/{id}")
async def delete_product_discount_endpoint(id: str):
    return await delete_product_discount(id)

# ---------------- ACTIVATE ----------------
@router.put("/{id}/activate")
async def activate_product_discount_endpoint(id: str):
    return await activate_product_discount(id)

# ---------------- DEACTIVATE ----------------
@router.put("/{id}/deactivate")
async def deactivate_product_discount_endpoint(id: str):
    return await deactivate_product_discount(id)

# ---------------- DATE RANGE FILTER ----------------
@router.get("/by_date_range")
async def list_product_discounts_by_date_range(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...)
):
    if start_date > end_date:
        raise HTTPException(400, "start_date cannot be after end_date")
    discounts = await get_product_discounts_by_date_range(start_date, end_date)
    return {"discounts": discounts}

@router.get("/active/last5")
async def list_last5_active_product_discounts():
    """
    Returns last 5 active product discounts with full details.
    """
    discounts = await get_last5_active_product_discounts()
    return {"discounts": discounts}
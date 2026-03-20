from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.faq_domain import FAQ
from app.services.faq_service import *

router = APIRouter()


class FAQCreate(BaseModel):
    question: str
    answer: str
    type: str
    category_id: Optional[str] = None
    product_id: Optional[str] = None
    sort_order: Optional[int] = 0


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


# CREATE
@router.post("/create")
async def create_faq_endpoint(payload: FAQCreate):
    faq = FAQ(**payload.model_dump())
    return {"status": "success", "data": await create_faq(faq)}


# LIST
@router.get("/list")
async def list_faqs():
    return {"status": "success", "data": await get_all_faqs()}


# PRODUCT FAQ
@router.get("/product")
async def product_faq(category_id: str, product_id: str):
    return {
        "status": "success",
        "data": await get_product_faqs(category_id, product_id)
    }


# CATEGORY FAQ
@router.get("/category/{category_id}")
async def category_faq(category_id: str):
    return {
        "status": "success",
        "data": await get_category_faqs(category_id)
    }


# UPDATE
@router.put("/{id}")
async def update_faq_endpoint(id: str, payload: FAQUpdate):
    updates = payload.model_dump(exclude_unset=True)
    return {"status": "success", "data": await update_faq(id, updates)}


# DELETE
@router.delete("/{id}")
async def delete_faq_endpoint(id: str):
    return {"status": "success", "data": await delete_faq(id)}
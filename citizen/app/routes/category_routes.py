from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.category_domain import Category
from app.services.category_service import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category,
    activate_category,
    deactivate_category,
    subcategory_base_categories
)

router = APIRouter()

# --------------------------
# Pydantic Models
# --------------------------
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_category_endpoint(payload: CategoryCreate):
    category = Category(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active
    )
    created = await create_category(category)
    return {"status": "success", "data": created}


# --------------------------
# LIST ALL
# --------------------------
@router.get("/list")
async def list_categories():
    categories = await get_all_categories()
    return {"status": "success", "categories": categories}

@router.get("/category_list")
async def list_subcategory_base_categories():
    categories = await subcategory_base_categories()
    return {"status": "success", "categories": categories}
# --------------------------
# GET BY ID
# --------------------------
@router.get("/{id}")
async def get_category_endpoint(id: str):
    category = await get_category_by_id(id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success", "data": category}


# --------------------------
# UPDATE
# --------------------------
@router.put("/{id}")
async def update_category_endpoint(id: str, payload: CategoryUpdate):
    update_data = payload.model_dump(exclude_unset=True)  # Pydantic v2
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    category = await update_category(id, update_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"status": "success", "data": category}


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_category_endpoint(id: str):
    result = await delete_category(id)
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success", "deleted_id": id}


# --------------------------
# ACTIVATE
# --------------------------
@router.put("/{id}/activate")
async def activate_category_endpoint(id: str):
    result = await activate_category(id)
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success", "data": result}


# --------------------------
# DEACTIVATE    
# --------------------------
@router.put("/{id}/deactivate")
async def deactivate_category_endpoint(id: str):
    result = await deactivate_category(id)
    if not result:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success", "data": result}
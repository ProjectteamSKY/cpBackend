from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.resource_domain import Resource
from app.services.resource_service import (
    create_resource,
    get_all_resources,
    get_resource_by_id,
    update_resource,
    delete_resource,
    activate_resource,
    deactivate_resource,
)

router = APIRouter()

# -------------------------- #
# Pydantic Models
# -------------------------- #
class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

# -------------------------- #
# CREATE
# -------------------------- #
@router.post("/create")
async def create_resource_endpoint(payload: ResourceCreate):
    resource = Resource(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    created = await create_resource(resource)
    return {"status": "success", "data": created}

# -------------------------- #
# LIST ALL
# -------------------------- #
@router.get("/list")
async def list_resources():
    resources = await get_all_resources()
    return {"status": "success", "resources": resources}

# -------------------------- #
# GET BY ID
# -------------------------- #
@router.get("/{id}")
async def get_resource_endpoint(id: str):
    resource = await get_resource_by_id(id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success", "data": resource}

# -------------------------- #
# UPDATE
# -------------------------- #
@router.put("/{id}")
async def update_resource_endpoint(id: str, payload: ResourceUpdate):
    update_data = payload.model_dump(exclude_unset=True)  # Pydantic v2
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    resource = await update_resource(id, update_data)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success", "data": resource}

# -------------------------- #
# DELETE
# -------------------------- #
@router.delete("/{id}")
async def delete_resource_endpoint(id: str):
    result = await delete_resource(id)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success", "deleted_id": id}

# -------------------------- #
# ACTIVATE
# -------------------------- #
@router.put("/{id}/activate")
async def activate_resource_endpoint(id: str):
    result = await activate_resource(id)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success", "data": result}

# -------------------------- #
# DEACTIVATE
# -------------------------- #
@router.put("/{id}/deactivate")
async def deactivate_resource_endpoint(id: str):
    result = await deactivate_resource(id)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success", "data": result}
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.permission_domain import Permission
from app.services.permission_service import (
    create_permission,
    get_all_permissions,
    get_permission_by_id,
    update_permission,
    delete_permission,
    activate_permission,
    deactivate_permission,
)

router = APIRouter()

# -------------------------- #
# Pydantic Models
# -------------------------- #
class PermissionCreate(BaseModel):
    resource_id: Optional[str] = None
    action: str
    method: str
    path: str
    description: Optional[str] = None
    is_active: bool = True

class PermissionUpdate(BaseModel):
    resource_id: Optional[str] = None
    action: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

# -------------------------- #
# CREATE
# -------------------------- #
@router.post("/create")
async def create_permission_endpoint(payload: PermissionCreate):
    permission = Permission(
        resource_id=payload.resource_id,
        action=payload.action,
        method=payload.method,
        path=payload.path,
        description=payload.description,
        is_active=payload.is_active,
    )
    created = await create_permission(permission)
    return {"status": "success", "data": created}

# -------------------------- #
# LIST ALL
# -------------------------- #
@router.get("/list")
async def list_permissions():
    permissions = await get_all_permissions()
    return {"status": "success", "permissions": permissions}

# -------------------------- #
# GET BY ID
# -------------------------- #
@router.get("/{id}")
async def get_permission_endpoint(id: str):
    permission = await get_permission_by_id(id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"status": "success", "data": permission}

# -------------------------- #
# UPDATE
# -------------------------- #
@router.put("/{id}")
async def update_permission_endpoint(id: str, payload: PermissionUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    permission = await update_permission(id, update_data)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"status": "success", "data": permission}

# -------------------------- #
# DELETE
# -------------------------- #
@router.delete("/{id}")
async def delete_permission_endpoint(id: str):
    result = await delete_permission(id)
    if not result:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"status": "success", "deleted_id": id}

# -------------------------- #
# ACTIVATE
# -------------------------- #
@router.put("/{id}/activate")
async def activate_permission_endpoint(id: str):
    result = await activate_permission(id)
    if not result:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"status": "success", "data": result}

# -------------------------- #
# DEACTIVATE
# -------------------------- #
@router.put("/{id}/deactivate")
async def deactivate_permission_endpoint(id: str):
    result = await deactivate_permission(id)
    if not result:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"status": "success", "data": result}
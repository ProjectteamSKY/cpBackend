from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.role_permission_domain import RolePermission
from app.services.role_permission_service import (
    create_role_permission,
    get_all_role_permissions,
    get_role_permission_by_id,
    get_role_permissions_by_role,
    get_role_permissions_by_permission,
    update_role_permission,
    delete_role_permission,
)

router = APIRouter()

# -------------------------- #
# Pydantic Models
# -------------------------- #
class RolePermissionCreate(BaseModel):
    role_id: str
    permission_id: str

class RolePermissionUpdate(BaseModel):
    role_id: Optional[str] = None
    permission_id: Optional[str] = None

# -------------------------- #
# CREATE / ASSIGN
# -------------------------- #
@router.post("/assign")
async def assign_role_permission(payload: RolePermissionCreate):
    rp = RolePermission(
        role_id=payload.role_id,
        permission_id=payload.permission_id,
    )
    created = await create_role_permission(rp)
    return {"status": "success", "data": created}

# -------------------------- #
# LIST ALL
# -------------------------- #
@router.get("/list")
async def list_role_permissions():
    data = await get_all_role_permissions()
    return {"status": "success", "role_permissions": data}

# -------------------------- #
# GET BY ID
# -------------------------- #
@router.get("/{id}")
async def get_role_permission_endpoint(id: str):
    rp = await get_role_permission_by_id(id)
    if not rp:
        raise HTTPException(status_code=404, detail="Role permission not found")
    return {"status": "success", "data": rp}

# -------------------------- #
# GET BY ROLE
# -------------------------- #
@router.get("/role/{role_id}")
async def get_role_permissions_for_role(role_id: str):
    data = await get_role_permissions_by_role(role_id)
    return {"status": "success", "data": data}

# -------------------------- #
# GET BY PERMISSION
# -------------------------- #
@router.get("/permission/{permission_id}")
async def get_role_permissions_for_permission(permission_id: str):
    data = await get_role_permissions_by_permission(permission_id)
    return {"status": "success", "data": data}

# -------------------------- #
# UPDATE
# -------------------------- #
@router.put("/{id}")
async def update_role_permission_endpoint(id: str, payload: RolePermissionUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    rp = await update_role_permission(id, update_data)
    if not rp:
        raise HTTPException(status_code=404, detail="Role permission not found")
    return {"status": "success", "data": rp}

# -------------------------- #
# DELETE
# -------------------------- #
@router.delete("/{id}")
async def delete_role_permission_endpoint(id: str):
    result = await delete_role_permission(id)
    if not result:
        raise HTTPException(status_code=404, detail="Role permission not found")
    return {"status": "success", "deleted_id": id}
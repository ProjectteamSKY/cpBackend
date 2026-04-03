from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.role_domain import Role
from app.services.role_service import (
    create_role,
    get_all_roles,
    get_role_by_id,
    update_role,
    delete_role,
    activate_role,
    deactivate_role,
)

router = APIRouter()

# -------------------------- #
# Pydantic Models
# -------------------------- #
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

# -------------------------- #
# CREATE
# -------------------------- #
@router.post("/create")
async def create_role_endpoint(payload: RoleCreate):
    role = Role(
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    created = await create_role(role)
    return {"status": "success", "data": created}

# -------------------------- #
# LIST ALL
# -------------------------- #
@router.get("/list")
async def list_roles():
    roles = await get_all_roles()
    return {"status": "success", "roles": roles}

# -------------------------- #
# GET BY ID
# -------------------------- #
@router.get("/{id}")
async def get_role_endpoint(id: str):
    role = await get_role_by_id(id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"status": "success", "data": role}

# -------------------------- #
# UPDATE
# -------------------------- #
@router.put("/{id}")
async def update_role_endpoint(id: str, payload: RoleUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    role = await update_role(id, update_data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"status": "success", "data": role}

# -------------------------- #
# DELETE
# -------------------------- #
@router.delete("/{id}")
async def delete_role_endpoint(id: str):
    result = await delete_role(id)
    if not result:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"status": "success", "deleted_id": id}

# -------------------------- #
# ACTIVATE
# -------------------------- #
@router.put("/{id}/activate")
async def activate_role_endpoint(id: str):
    result = await activate_role(id)
    if not result:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"status": "success", "data": result}

# -------------------------- #
# DEACTIVATE
# -------------------------- #
@router.put("/{id}/deactivate")
async def deactivate_role_endpoint(id: str):
    result = await deactivate_role(id)
    if not result:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"status": "success", "data": result}
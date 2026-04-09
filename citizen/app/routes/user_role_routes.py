from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.user_role_domain import UserRole
from app.services.user_role_service import (
    create_user_role,
    get_all_user_roles,
    get_user_role_by_id,
    get_user_roles_by_user,
    update_user_role,
    delete_user_role,
)

router = APIRouter()

# -------------------------- #
# Pydantic Models
# -------------------------- #
class UserRoleCreate(BaseModel):
    user_id: str
    role_id: str
    assigned_by: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role_id: Optional[str] = None
    assigned_by: Optional[str] = None

# -------------------------- #
# CREATE / ASSIGN
# -------------------------- #
@router.post("/assign")
async def assign_user_role(payload: UserRoleCreate):
    user_role = UserRole(
        user_id=payload.user_id,
        role_id=payload.role_id,
        assigned_by=payload.assigned_by,
    )
    created = await create_user_role(user_role)
    return {"status": "success", "data": created}

# -------------------------- #
# LIST ALL
# -------------------------- #
@router.get("/list")
async def list_user_roles():
    roles = await get_all_user_roles()
    return {"status": "success", "user_roles": roles}

# -------------------------- #
# GET BY ID
# -------------------------- #
@router.get("/{id}")
async def get_user_role_endpoint(id: str):
    role = await get_user_role_by_id(id)
    if not role:
        raise HTTPException(status_code=404, detail="User role not found")
    return {"status": "success", "data": role}

# -------------------------- #
# GET BY USER
# -------------------------- #
@router.get("/user/{user_id}")
async def get_user_roles_for_user(user_id: str):
    roles = await get_user_roles_by_user(user_id)
    return {"status": "success", "data": roles}

# -------------------------- #
# UPDATE
# -------------------------- #
@router.put("/{id}")
async def update_user_role_endpoint(id: str, payload: UserRoleUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    role = await update_user_role(id, update_data)
    if not role:
        raise HTTPException(status_code=404, detail="User role not found")
    return {"status": "success", "data": role}

# -------------------------- #
# DELETE
# -------------------------- #
@router.delete("/{id}")
async def delete_user_role_endpoint(id: str):
    result = await delete_user_role(id)
    if not result:
        raise HTTPException(status_code=404, detail="User role not found")
    return {"status": "success", "deleted_id": id}
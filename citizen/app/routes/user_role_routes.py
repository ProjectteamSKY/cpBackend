from fastapi import APIRouter, Form, HTTPException
from app.domain.user_role_domain import UserRole
from app.services.user_role_service import (
    assign_role_service,
    get_roles_by_user_service,
    remove_role_service,
    get_all_users_with_roles_service
)

router = APIRouter(prefix="/user-roles", tags=["User Roles"])

@router.post("/assign")
async def assign_role(
    user_id: int = Form(...),
    role_id: int = Form(...),
    assigned_by: str | None = Form(None),
):
    assigned_by_int = int(assigned_by) if assigned_by not in (None, "", "null") else None
    ur = UserRole(user_id, role_id, assigned_by_int)
    return await assign_role_service(ur)


@router.get("/users-withroles")
async def get_all_users_with_roles():
    return await get_all_users_with_roles_service()


@router.get("/{user_id}")
async def get_roles(user_id: int):
    return await get_roles_by_user_service(user_id)


@router.delete("/remove")
async def remove_role(
    user_id: int = Form(...),
    role_id: int = Form(...),
):
    removed = await remove_role_service(user_id, role_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Role not assigned")
    return {"message": "Role removed"}
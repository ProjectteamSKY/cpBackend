from fastapi import APIRouter, Form, HTTPException
from app.domain.role_permission_domain import RolePermission
from app.services.role_permission_service import (
    assign_role_permission_service,
    get_permissions_by_role_service,
    remove_role_permission_service,
    get_all_role_permissions_service,
)

router = APIRouter(prefix="/role-permissions", tags=["Role Permissions"])


@router.get("/")
async def get_all_role_permissions():
    return await get_all_role_permissions_service()


@router.post("/assign")
async def assign_permission(role_id: int = Form(...), permission_id: int = Form(...)):
    return await assign_role_permission_service(RolePermission(role_id, permission_id))


@router.get("/{role_id}")
async def get_permissions(role_id: int):
    return await get_permissions_by_role_service(role_id)


@router.delete("/remove")
async def remove_permission(role_id: int = Form(...), permission_id: int = Form(...)):
    removed = await remove_role_permission_service(role_id, permission_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Permission not assigned")
    return {"message": "Permission removed"}
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.role_permission_domain import RolePermission
from app.services import role_permission_service

router = APIRouter(prefix="/role-permissions", tags=["Role Permissions"])


@router.post("/assign")
async def assign_permission(
    role_id: str = Form(...),
    permission_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    role_permission = RolePermission(
        role_id=role_id,
        permission_id=permission_id,
    )

    return await role_permission_service.assign_permission(role_permission, session)


@router.get("/role/{role_id}")
async def get_permissions(role_id: str, session: AsyncSession = Depends(get_session)):
    return await role_permission_service.get_permissions_by_role(role_id, session)


@router.get("/permission/{permission_id}")
async def get_roles(permission_id: str, session: AsyncSession = Depends(get_session)):
    return await role_permission_service.get_roles_by_permission(permission_id, session)


@router.delete("/remove")
async def remove_permission(
    role_id: str = Form(...),
    permission_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    removed = await role_permission_service.remove_permission(
        role_id, permission_id, session
    )

    if not removed:
        raise HTTPException(status_code=404, detail="Mapping not found")

    return {"message": "Permission removed from role"}
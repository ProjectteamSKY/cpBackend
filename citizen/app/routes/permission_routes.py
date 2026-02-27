from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services import permission_service
from app.domain.permission_domain import Permission

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/", status_code=201)
async def create_permission(
    resource_id: str = Form(...),
    action: str = Form(...),
    method: str = Form(...),
    path: str = Form(...),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session),
):
    permission = Permission(
        resource_id=resource_id,
        action=action,
        method=method,
        path=path,
        description=description,
    )

    return await permission_service.create_permission(permission, session)


@router.get("/")
async def get_all_permissions(session: AsyncSession = Depends(get_session)):
    return await permission_service.get_all_permissions(session)


@router.get("/{permission_id}")
async def get_permission(permission_id: str, session: AsyncSession = Depends(get_session)):
    permission = await permission_service.get_permission_by_id(permission_id, session)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.delete("/{permission_id}")
async def delete_permission(permission_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await permission_service.delete_permission(permission_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted successfully"}
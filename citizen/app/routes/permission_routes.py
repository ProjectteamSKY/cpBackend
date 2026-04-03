from fastapi import APIRouter, Form, HTTPException
from app.domain.permission_domain import Permission
from app.services.permission_service import (
    create_permission,
    get_all_permissions,
    delete_permission,
)

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/create")
async def create_permission_route(
    resource_id: int = Form(...),
    action: str = Form(...),
    method: str = Form(...),
    path: str = Form(...),
    description: str = Form(None),
):
    permission = Permission(
        resource_id=resource_id,
        action=action,
        method=method,
        path=path,
        description=description,
    )
    return await create_permission(permission)


@router.get("/")
async def list_permissions():
    return await get_all_permissions()


@router.delete("/delete")
async def delete_permission_route(permission_id: int = Form(...)):
    deleted = await delete_permission(permission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted"}
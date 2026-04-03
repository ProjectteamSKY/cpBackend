from fastapi import APIRouter, Form, HTTPException
from app.domain.role_domain import Role
from app.services.role_service import create_role, get_all_roles, delete_role

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/create")
async def create_role_route(name: str = Form(...), description: str = Form(None)):
    return await create_role(Role(name, description))


@router.get("/")
async def list_roles():
    return await get_all_roles()


@router.delete("/delete")
async def delete_role_route(role_id: int = Form(...)):
    deleted = await delete_role(role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted", "role": deleted}
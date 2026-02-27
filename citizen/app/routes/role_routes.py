from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services import role_service
from app.domain.role_domain import Role

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", status_code=201)
async def create_role(
    name: str = Form(...),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session),
):
    existing = await role_service.get_role_by_name(name, session)
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Role(name=name, description=description)

    return await role_service.create_role(role, session)


@router.get("/")
async def get_all_roles(session: AsyncSession = Depends(get_session)):
    return await role_service.get_all_roles(session)


@router.get("/{role_id}")
async def get_role(role_id: str, session: AsyncSession = Depends(get_session)):
    role = await role_service.get_role_by_id(role_id, session)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/{role_id}")
async def delete_role(role_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await role_service.delete_role(role_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.user_role_domain import UserRole
from app.services import user_role_service

router = APIRouter(prefix="/user-roles", tags=["User Roles"])


@router.post("/assign")
async def assign_role(
    user_id: str = Form(...),
    role_id: str = Form(...),
    assigned_by: str = Form(None),
    session: AsyncSession = Depends(get_session),
):
    user_role = UserRole(
        user_id=user_id,
        role_id=role_id,
        assigned_by=assigned_by,
    )

    return await user_role_service.assign_role(user_role, session)


@router.get("/user/{user_id}")
async def get_roles(user_id: str, session: AsyncSession = Depends(get_session)):
    return await user_role_service.get_roles_by_user(user_id, session)


@router.get("/role/{role_id}")
async def get_users(role_id: str, session: AsyncSession = Depends(get_session)):
    return await user_role_service.get_users_by_role(role_id, session)


@router.delete("/remove")
async def remove(
    user_id: str = Form(...),
    role_id: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    removed = await user_role_service.remove_role(user_id, role_id, session)

    if not removed:
        raise HTTPException(status_code=404, detail="Mapping not found")

    return {"message": "Role removed from user"}
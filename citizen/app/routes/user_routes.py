from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.user_schema import RegisterSchema, LoginSchema
from app.services.user_service import register_user, login_user

router = APIRouter()


@router.post("/register")
async def register(data: RegisterSchema, session: AsyncSession = Depends(get_session)):

    user = await register_user(data, session)

    if not user:
        raise HTTPException(400, "Email already exists")

    return user


@router.post("/login")
async def login(data: LoginSchema, session: AsyncSession = Depends(get_session)):

    result = await login_user(data, session)

    if not result:
        raise HTTPException(401, "Invalid credentials")

    return result

@router.post("/login1236456356")
async def login(data: LoginSchema, session: AsyncSession = Depends(get_session)):

    result = await login_user(data, session)

    if not result:
        raise HTTPException(401, "Invalid credentials")

    return result


@router.post("/login12364566756756356")
async def login(data: LoginSchema, session: AsyncSession = Depends(get_session)):

    result = await login_user(data, session)

    if not result:
        raise HTTPException(401, "Invalid credentials")

    return result

@router.post("/logintest")
async def login(data: LoginSchema, session: AsyncSession = Depends(get_session)):

    result = await login_user(data, session)

    if not result:
        raise HTTPException(401, "Invalid credentials")

    return result
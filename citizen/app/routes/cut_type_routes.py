from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.domain.cut_type_domain import CutType

from app.services.cut_type_service import (
    create_cut_type,
    get_all_cut_types,
    get_cut_type_by_id,
    update_cut_type,
    delete_cut_type,
    activate_cut_type,
    deactivate_cut_type,
    get_all_cut_types_active
)

router = APIRouter()


@router.post("/create")
async def create_cut_type_endpoint(
    name: str = Form(...),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session)
):

    cut_type = CutType(
        name=name,
        description=description
    )

    return await create_cut_type(cut_type, session)


@router.get("/list")
async def list_cut_types(
    session: AsyncSession = Depends(get_session)
):

    return {
        "cut_types": await get_all_cut_types(session)
    }

@router.get("/list/active")
async def list_cut_types_active(
    session: AsyncSession = Depends(get_session)
):

    return {
        "cut_types": await get_all_cut_types_active(session)
    }

@router.get("/{id}")
async def get_cut_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await get_cut_type_by_id(id, session)

    if not result:
        raise HTTPException(404, "Cut Type not found")

    return result


@router.put("/{id}")
async def update_cut_type_endpoint(
    id: str,
    name: str = Form(...),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session)
):

    result = await update_cut_type(
        id,
        name,
        description,
        session
    )

    if not result:
        raise HTTPException(404, "Cut Type not found")

    return result


@router.delete("/{id}")
async def delete_cut_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await delete_cut_type(id, session)


@router.put("/{id}/activate")
async def activate_cut_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await activate_cut_type(id, session)


@router.put("/{id}/deactivate")
async def deactivate_cut_type_endpoint(id: str, session: AsyncSession = Depends(get_session)):
    result = await deactivate_cut_type(id, session)
    if not result:
        raise HTTPException(404, "Cut Type not found or already inactive")
    return result
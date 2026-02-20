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
    activate_cut_type
)

router = APIRouter()


@router.post("/cut-type/create")
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


@router.get("/cut-types/list")
async def list_cut_types(
    session: AsyncSession = Depends(get_session)
):

    return {
        "cut_types": await get_all_cut_types(session)
    }


@router.get("/cut-type/{id}")
async def get_cut_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await get_cut_type_by_id(id, session)

    if not result:
        raise HTTPException(404, "Cut Type not found")

    return result


@router.put("/cut-type/{id}")
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


@router.delete("/cut-type/{id}")
async def delete_cut_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await delete_cut_type(id, session)


@router.put("/cut-type/{id}/activate")
async def activate_cut_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    return await activate_cut_type(id, session)
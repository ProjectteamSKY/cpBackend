from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.schemas.cut_type_schema import *
from app.services.cut_type_service import *

router = APIRouter(
)


@router.post("/", response_model=CutTypeResponse)
async def create_cut_type(
    data: CutTypeCreate,
    session: AsyncSession = Depends(get_session)
):

    return await create_cut_type_service(
        session,
        data.name,
        data.description
    )


@router.get("/", response_model=list[CutTypeResponse])
async def get_cut_types(
    session: AsyncSession = Depends(get_session)
):

    return await get_all_cut_types_service(session)


@router.get("/{cut_type_id}", response_model=CutTypeResponse)
async def get_cut_type(
    cut_type_id: str,
    session: AsyncSession = Depends(get_session)
):

    cut_type = await get_cut_type_service(session, cut_type_id)

    if not cut_type:
        raise HTTPException(404, "Cut type not found")

    return cut_type


@router.put("/{cut_type_id}", response_model=CutTypeResponse)
async def update_cut_type(
    cut_type_id: str,
    data: CutTypeUpdate,
    session: AsyncSession = Depends(get_session)
):

    return await update_cut_type_service(
        session,
        cut_type_id,
        data.dict(exclude_unset=True)
    )


@router.delete("/{cut_type_id}")
async def delete_cut_type(
    cut_type_id: str,
    session: AsyncSession = Depends(get_session)
):

    await delete_cut_type_service(session, cut_type_id)

    return {"message": "Cut type deleted successfully"}

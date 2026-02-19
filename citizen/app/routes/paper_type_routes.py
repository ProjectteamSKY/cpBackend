from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.schemas.paper_type_schema import (
    PaperTypeCreateSchema,
    PaperTypeUpdateSchema,
    PaperTypeResponseSchema
)

from app.services.paper_type_service import (
    create_paper_type,
    get_paper_type,
    get_all_paper_types,
    update_paper_type,
    delete_paper_type
)


router = APIRouter()


# CREATE
@router.post("/", response_model=PaperTypeResponseSchema)
async def create_route(
    data: PaperTypeCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    return await create_paper_type(data, session)


# GET ALL
@router.get("/", response_model=list[PaperTypeResponseSchema])
async def get_all_route(
    session: AsyncSession = Depends(get_session)
):
    return await get_all_paper_types(session)


# GET ONE
@router.get("/{pt_id}", response_model=PaperTypeResponseSchema)
async def get_route(
    pt_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await get_paper_type(pt_id, session)


# UPDATE
@router.put("/{pt_id}", response_model=PaperTypeResponseSchema)
async def update_route(
    pt_id: str,
    data: PaperTypeUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    return await update_paper_type(pt_id, data, session)


# DELETE
@router.delete("/{pt_id}")
async def delete_route(
    pt_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await delete_paper_type(pt_id, session)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.cut_type_schema import CutTypeCreateSchema, CutTypeResponseSchema
from app.services.cut_type_service import create_cut_type, get_cut_type

router = APIRouter()

@router.post("/", response_model=CutTypeResponseSchema)
async def create_cut_type_route(data: CutTypeCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_cut_type(data, session)

@router.get("/{cut_type_id}", response_model=CutTypeResponseSchema)
async def get_cut_type_route(cut_type_id: str, session: AsyncSession = Depends(get_session)):
    cut_type = await get_cut_type(cut_type_id, session)
    if not cut_type:
        raise HTTPException(404, "CutType not found")
    return cut_type

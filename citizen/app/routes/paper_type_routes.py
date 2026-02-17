from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.paper_type_schema import PaperTypeCreateSchema, PaperTypeResponseSchema
from app.services.paper_type_service import create_paper_type, get_paper_type

router = APIRouter(prefix="/paper-types", tags=["PaperTypes"])

@router.post("/", response_model=PaperTypeResponseSchema)
async def create_paper_type_route(data: PaperTypeCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_paper_type(data, session)

@router.get("/{pt_id}", response_model=PaperTypeResponseSchema)
async def get_paper_type_route(pt_id: str, session: AsyncSession = Depends(get_session)):
    pt = await get_paper_type(pt_id, session)
    if not pt:
        raise HTTPException(404, "PaperType not found")
    return pt

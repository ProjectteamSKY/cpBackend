from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.finish_schema import FinishCreateSchema, FinishResponseSchema
from app.services.finish_service import create_finish, get_finish

router = APIRouter()

@router.post("/", response_model=FinishResponseSchema)
async def create_finish_route(data: FinishCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_finish(data, session)

@router.get("/{finish_id}", response_model=FinishResponseSchema)
async def get_finish_route(finish_id: str, session: AsyncSession = Depends(get_session)):
    finish = await get_finish(finish_id, session)
    if not finish:
        raise HTTPException(404, "Finish not found")
    return finish

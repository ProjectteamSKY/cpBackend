from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.schemas.finish_schema import (
    FinishCreateSchema,
    FinishUpdateSchema,
    FinishResponseSchema
)

from app.services.finish_service import (
    create_finish,
    get_finish,
    get_all_finishes,
    update_finish,
    delete_finish
)


router = APIRouter()


# CREATE
@router.post(
    "/",
    response_model=FinishResponseSchema
)
async def create_route(
    data: FinishCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    return await create_finish(
        data,
        session
    )


# GET ALL
@router.get(
    "/",
    response_model=list[FinishResponseSchema]
)
async def get_all_route(
    session: AsyncSession = Depends(get_session)
):
    return await get_all_finishes(
        session
    )


# GET ONE
@router.get(
    "/{finish_id}",
    response_model=FinishResponseSchema
)
async def get_route(
    finish_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await get_finish(
        finish_id,
        session
    )


# UPDATE
@router.put(
    "/{finish_id}",
    response_model=FinishResponseSchema
)
async def update_route(
    finish_id: str,
    data: FinishUpdateSchema,
    session: AsyncSession = Depends(get_session)
):
    return await update_finish(
        finish_id,
        data,
        session
    )


# DELETE
@router.delete("/{finish_id}")
async def delete_route(
    finish_id: str,
    session: AsyncSession = Depends(get_session)
):
    return await delete_finish(
        finish_id,
        session
    )

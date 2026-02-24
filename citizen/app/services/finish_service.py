from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.finish_domain import Finish

from app.repository.finish_repository import (
    create_finish_repo,
    get_finish_by_id_repo,
    get_all_finishes_repo,
    update_finish_repo,
    delete_finish_repo
)

from app.schemas.finish_schema import (
    FinishCreateSchema,
    FinishUpdateSchema
)


# CREATE
async def create_finish(
    data: FinishCreateSchema,
    session: AsyncSession
):

    finish = Finish(
        name=data.name,
        description=data.description
    )

    return await create_finish_repo(
        finish,
        session
    )


# GET ONE
async def get_finish(
    finish_id: str,
    session: AsyncSession
):

    finish = await get_finish_by_id_repo(
        finish_id,
        session
    )

    if not finish:
        raise HTTPException(
            status_code=404,
            detail="Finish not found"
        )

    return finish


# GET ALL
async def get_all_finishes(
    session: AsyncSession
):

    return await get_all_finishes_repo(
        session
    )


# UPDATE
async def update_finish(
    finish_id: str,
    data: FinishUpdateSchema,
    session: AsyncSession
):

    finish = await update_finish_repo(
        finish_id,
        data.model_dump(exclude_unset=True),
        session
    )

    if not finish:
        raise HTTPException(
            status_code=404,
            detail="Finish not found"
        )

    return finish


# DELETE
async def delete_finish(
    finish_id: str,
    session: AsyncSession
):

    success = await delete_finish_repo(
        finish_id,
        session
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Finish not found"
        )

    return {
        "message": "Finish deleted successfully"
    }

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.paper_type_domain import PaperType

from app.repository.paper_type_repository import (
    create_paper_type_repo,
    get_paper_type_by_id_repo,
    get_all_paper_types_repo,
    update_paper_type_repo,
    delete_paper_type_repo
)

from app.schemas.paper_type_schema import (
    PaperTypeCreateSchema,
    PaperTypeUpdateSchema
)


# CREATE
async def create_paper_type(
    data: PaperTypeCreateSchema,
    session: AsyncSession
):

    pt = PaperType(
        name=data.name,
        description=data.description
    )

    return await create_paper_type_repo(pt, session)


# GET ONE
async def get_paper_type(
    pt_id: str,
    session: AsyncSession
):

    pt = await get_paper_type_by_id_repo(pt_id, session)

    if not pt:
        raise HTTPException(404, "PaperType not found")

    return pt


# GET ALL
async def get_all_paper_types(session: AsyncSession):

    return await get_all_paper_types_repo(session)


# UPDATE
async def update_paper_type(
    pt_id: str,
    data: PaperTypeUpdateSchema,
    session: AsyncSession
):

    updated = await update_paper_type_repo(
        pt_id,
        data.model_dump(exclude_unset=True),
        session
    )

    if not updated:
        raise HTTPException(404, "PaperType not found")

    return updated


# DELETE
async def delete_paper_type(
    pt_id: str,
    session: AsyncSession
):

    success = await delete_paper_type_repo(pt_id, session)

    if not success:
        raise HTTPException(404, "PaperType not found")

    return {"message": "PaperType deleted successfully"}

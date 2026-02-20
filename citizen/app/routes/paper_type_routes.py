from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.domain.paper_type_domain import PaperType

from app.services.paper_type_service import (
    create_paper_type,
    get_all_paper_types,
    get_paper_type_by_id,
    update_paper_type,
    delete_paper_type,
    activate_paper_type,
    deactivate_paper_type
)


router = APIRouter()


# CREATE
@router.post("/paper-type/create")
async def create_paper_type_endpoint(
    name: str = Form(...),
    description: str = Form(None),
    is_active: bool = Form(True),
    session: AsyncSession = Depends(get_session)
):

    paper_type = PaperType(
        name=name,
        description=description,
        is_active=is_active
    )

    return await create_paper_type(paper_type, session)


# LIST
@router.get("/paper-types/list")
async def list_paper_types(
    session: AsyncSession = Depends(get_session)
):

    data = await get_all_paper_types(session)

    return {"paper_types": data}


# GET BY ID
@router.get("/paper-type/{id}")
async def get_paper_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    data = await get_paper_type_by_id(id, session)

    if not data:
        raise HTTPException(404, "Paper type not found")

    return data


# UPDATE
@router.put("/paper-type/{id}")
async def update_paper_type_endpoint(
    id: str,
    name: str = Form(None),
    description: str = Form(None),
    is_active: bool = Form(None),
    session: AsyncSession = Depends(get_session)
):

    payload = {}

    if name is not None:
        payload["name"] = name

    if description is not None:
        payload["description"] = description

    if is_active is not None:
        payload["is_active"] = is_active

    if not payload:
        raise HTTPException(400, "No fields to update")

    result = await update_paper_type(id, payload, session)

    if not result:
        raise HTTPException(404, "Paper type not found")

    return {
        "status": "success",
        "data": result
    }


# DELETE (SOFT)
@router.delete("/paper-type/{id}")
async def delete_paper_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await delete_paper_type(id, session)

    if not result:
        raise HTTPException(404, "Paper type not found")

    return {
        "status": "success",
        "deleted_id": id
    }


# ACTIVATE
@router.put("/paper-type/{id}/activate")
async def activate_paper_type_endpoint(
    id: str,
    session: AsyncSession = Depends(get_session)
):

    result = await activate_paper_type(id, session)

    if not result:
        raise HTTPException(404, "Paper type not found")

    return result
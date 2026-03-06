from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.domain.print_type_domain import PrintType

from app.services.print_type_service import (
    create_print_type,
    get_all_print_types,
    get_print_type_by_id,
    update_print_type,
    delete_print_type,
    activate_print_type,
    deactivate_print_type,
    get_all_print_types_active
)


router = APIRouter()


# CREATE
@router.post("/create")
async def create_print_type_endpoint(
    name: str = Form(...),
    description: str = Form(None),
    is_active: bool = Form(True),
):

    print_type = PrintType(
        name=name,
        description=description,
        is_active=is_active
    )

    return await create_print_type(print_type)


# LIST
@router.get("/list")
async def list_print_types(
):

    data = await get_all_print_types()

    return {"print_types": data}


@router.get("/list/active")
async def list_print_types(
):

    data = await get_all_print_types_active()

    return {"print_types": data}


# GET BY ID
@router.get("/{id}")
async def get_print_type_endpoint(
    id: str,
):

    data = await get_print_type_by_id(id)

    if not data:
        raise HTTPException(404, "Print type not found")

    return data


# UPDATE
@router.put("/{id}")
async def update_print_type_endpoint(
    id: str,
    name: str = Form(None),
    description: str = Form(None),
    is_active: bool = Form(None),
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

    result = await update_print_type(id, payload)

    if not result:
        raise HTTPException(404, "Print type not found")

    return {
        "status": "success",
        "data": result
    }


# DELETE (SOFT)
@router.delete("/{id}")
async def delete_print_type_endpoint(
    id: str,
):

    result = await delete_print_type(id)

    if not result:
        raise HTTPException(404, "Print type not found")

    return {
        "status": "success",
        "deleted_id": id
    }


# ACTIVATE
@router.put("/{id}/activate")
async def activate_print_type_endpoint(
    id: str,
):

    result = await activate_print_type(id)

    if not result:
        raise HTTPException(404, "Print type not found")

    return result


@router.put("/{id}/deactivate")
async def activate_print_type_endpoint(
    id: str,
):

    result = await deactivate_print_type(id)

    if not result:
        raise HTTPException(404, "Print type not found")

    return result
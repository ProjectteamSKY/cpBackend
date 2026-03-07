from typing import Optional
from fastapi import APIRouter, Form, HTTPException
from app.domain.paper_type_domain import PaperType
from app.services.paper_type_service import (
    create_paper_type,
    get_all_paper_types,
    get_all_paper_types_active,
    get_paper_type_by_id,
    update_paper_type,
    delete_paper_type,
    activate_paper_type,
    deactivate_paper_type
)

router = APIRouter()



# --------------------------
# CREATE
# --------------------------
@router.post("/create")
async def create_paper_type_endpoint(
    name: str = Form(...),
    gsm: float = Form(300),
    description: Optional[str] = Form(None),
    is_active: bool = Form(True)
):
    paper_type = PaperType(
        name=name,
        gsm=gsm,
        description=description,
        is_active=is_active
    )

    created = await create_paper_type(paper_type)

    return {
        "status": "success",
        "data": created
    }



# --------------------------
# LIST ALL
# --------------------------
@router.get("/list")
async def list_paper_types():
    data = await get_all_paper_types()
    return {"status": "success", "paper_types": data}



@router.get("/list/active")
async def list_paper_types_active():
    data = await get_all_paper_types_active()
    return {"status": "success", "paper_types": data}



# --------------------------
# GET BY ID
# --------------------------
@router.get("/{id}")
async def get_paper_type_endpoint(id: str):
    data = await get_paper_type_by_id(id)

    if not data:
        raise HTTPException(status_code=404, detail="Paper type not found")

    return {"status": "success", "data": data}



# --------------------------
# UPDATE
# --------------------------
@router.put("/{id}")
async def update_paper_type_endpoint(
    id: str,
    name: Optional[str] = Form(None),
    gsm: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None)
):

    update_data = {}

    if name is not None:
        update_data["name"] = name

    if gsm is not None:
        update_data["gsm"] = gsm

    if description is not None:
        update_data["description"] = description

    if is_active is not None:
        update_data["is_active"] = is_active

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await update_paper_type(id, update_data)

    if not result:
        raise HTTPException(status_code=404, detail="Paper type not found")

    return {"status": "success", "data": result}



# --------------------------
# DELETE
# --------------------------
@router.delete("/{id}")
async def delete_paper_type_endpoint(id: str):

    result = await delete_paper_type(id)

    if not result:
        raise HTTPException(status_code=404, detail="Paper type not found")

    return {"status": "success", "deleted_id": id}



# --------------------------
# ACTIVATE
# --------------------------
@router.put("/{id}/activate")
async def activate_paper_type_endpoint(id: str):

    result = await activate_paper_type(id)

    if not result:
        raise HTTPException(status_code=404, detail="Paper type not found")

    return {"status": "success", "data": result}



# --------------------------
# DEACTIVATE
# --------------------------
@router.put("/{id}/deactivate")
async def deactivate_paper_type_endpoint(id: str):

    result = await deactivate_paper_type(id)

    if not result:
        raise HTTPException(status_code=404, detail="Paper type not found")

    return {"status": "success", "data": result}

from fastapi import APIRouter, HTTPException, Form
from app.domain.resource_domain import Resource
from app.services.resource_service import (
    create_resource,
    get_all_resources,
    get_resource_by_id,
    delete_resource,
)

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("/")
async def add_resource(name: str = Form(...), description: str = Form(None)):
    return await create_resource(Resource(name, description))


@router.get("/")
async def list_resources():
    return await get_all_resources()


@router.get("/{resource_id}")
async def get_resource(resource_id: int):
    resource = await get_resource_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


# @router.put("/{resource_id}")
# async def edit_resource(resource_id: int, name: str = Form(...), description: str = Form(None)):
#     updated = await update_resource(resource_id, Resource(name, description))
#     if not updated:
#         raise HTTPException(status_code=404, detail="Resource not found")
#     return updated


@router.delete("/{resource_id}")
async def remove_resource(resource_id: int):
    deleted = await delete_resource(resource_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted", "resource": deleted}
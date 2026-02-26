from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services import resource_service
from app.domain.resource_domain import Resource

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("/", status_code=201)
async def create_resource(
    name: str = Form(...),
    description: str = Form(None),
    session: AsyncSession = Depends(get_session),
):
    existing = await resource_service.get_resource_by_name(name, session)
    if existing:
        raise HTTPException(status_code=400, detail="Resource already exists")

    resource = Resource(name=name, description=description)

    return await resource_service.create_resource(resource, session)


@router.get("/")
async def get_all_resources(session: AsyncSession = Depends(get_session)):
    return await resource_service.get_all_resources(session)


@router.get("/{resource_id}")
async def get_resource(resource_id: str, session: AsyncSession = Depends(get_session)):
    resource = await resource_service.get_resource_by_id(resource_id, session)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await resource_service.delete_resource(resource_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}
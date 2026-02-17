from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.sheet_template_schema import SheetTemplateCreateSchema, SheetTemplateResponseSchema
from app.services.sheet_template_service import create_sheet_template, get_sheet_template

router = APIRouter(prefix="/sheet-templates", tags=["SheetTemplates"])

@router.post("/", response_model=SheetTemplateResponseSchema)
async def create_sheet_template_route(data: SheetTemplateCreateSchema, session: AsyncSession = Depends(get_session)):
    return await create_sheet_template(data, session)

@router.get("/{template_id}", response_model=SheetTemplateResponseSchema)
async def get_sheet_template_route(template_id: str, session: AsyncSession = Depends(get_session)):
    template = await get_sheet_template(template_id, session)
    if not template:
        raise HTTPException(404, "SheetTemplate not found")
    return template

from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.sheet_template_repository import create_sheet_template_repo, get_sheet_template_by_id_repo
from app.domain.sheet_template_domain import SheetTemplate as SheetTemplateDomain

async def create_sheet_template(data, session: AsyncSession):
    template = SheetTemplateDomain(
        sheet_type=data.sheet_type,
        card_width=data.card_width,
        card_height=data.card_height,
        max_cards_per_sheet=data.max_cards_per_sheet
    )
    return await create_sheet_template_repo(template, session)

async def get_sheet_template(template_id: str, session: AsyncSession):
    return await get_sheet_template_by_id_repo(template_id, session)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.product_models import SheetTemplate as SheetTemplateORM
from app.domain.sheet_template_domain import SheetTemplate as SheetTemplateDomain

async def create_sheet_template_repo(template: SheetTemplateDomain, session: AsyncSession):
    orm = SheetTemplateORM(
        id=template.id,
        sheet_type=template.sheet_type,
        card_width=template.card_width,
        card_height=template.card_height,
        max_cards_per_sheet=template.max_cards_per_sheet
    )
    session.add(orm)
    await session.commit()
    await session.refresh(orm)
    return SheetTemplateDomain(
        id=orm.id,
        sheet_type=orm.sheet_type,
        card_width=orm.card_width,
        card_height=orm.card_height,
        max_cards_per_sheet=orm.max_cards_per_sheet
    )

async def get_sheet_template_by_id_repo(template_id: str, session: AsyncSession):
    result = await session.execute(select(SheetTemplateORM).where(SheetTemplateORM.id == template_id))
    orm = result.scalar_one_or_none()
    if not orm:
        return None
    return SheetTemplateDomain(
        id=orm.id,
        sheet_type=orm.sheet_type,
        card_width=orm.card_width,
        card_height=orm.card_height,
        max_cards_per_sheet=orm.max_cards_per_sheet
    )

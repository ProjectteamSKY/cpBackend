from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user_model import User


async def create_user_repo(user: User, session: AsyncSession):
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_email_repo(email: str, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id_repo(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

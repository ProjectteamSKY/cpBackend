from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.password_token_domain import PasswordResetToken
from app.utils.query_loader import load_queries

queries = load_queries()

async def create_token(token_obj: PasswordResetToken, session: AsyncSession):
    params = {
        "user_id": token_obj.user_id,
        "token": token_obj.token,
        "expires_at": token_obj.expires_at,
    }
    result = await session.execute(text(queries.create_token), params)
    await session.commit()
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_token(token: str, session: AsyncSession):
    result = await session.execute(
        text(queries.get_token), {"token": token}
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def mark_token_used(token: str, session: AsyncSession):
    result = await session.execute(
        text(queries.mark_used), {"token": token}
    )
    await session.commit()
    return bool(result.fetchone())

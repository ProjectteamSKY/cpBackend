import hashlib
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.user_domain import User
from app.utils.query_loader import load_queries

queries = load_queries()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def create_user(user: User, session: AsyncSession):
    await session.execute(
        text(queries["user"]["create_user"]),
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "contact": user.contact,
            "password_hash": hash_password(user.password),
        },
    )
    await session.commit()

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "contact": user.contact,
        "is_active": True,
    }


async def get_user_by_email(email: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user"]["get_by_email"]),
        {"email": email},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_user_by_id(user_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user"]["get_by_id"]),
        {"user_id": user_id},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def get_all_users(session: AsyncSession):
    result = await session.execute(text(queries["user"]["get_all"]))
    return [dict(r._mapping) for r in result.fetchall()]


async def delete_user(user_id: str, session: AsyncSession):
    result = await session.execute(
        text(queries["user"]["delete_user"]),
        {"user_id": user_id},
    )
    await session.commit()
    return result.rowcount > 0


async def login_user(email: str, password: str, session: AsyncSession):
    user = await get_user_by_email(email, session)
    if not user:
        return None

    hashed = hash_password(password)
    if hashed != user["password_hash"]:
        return None

    token = secrets.token_hex(32)

    await session.execute(
        text(queries["user"]["update_token"]),
        {"token": token, "id": user["id"]},
    )
    await session.commit()

    return {
        "id": user["id"],
        "email": user["email"],
        "token": token,
    }
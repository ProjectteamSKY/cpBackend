import hashlib
import secrets

from app.domain.user_domain import User
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


async def create_user(user: User):
    await execute(
        queries["user"]["create_user"],
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "contact": user.contact,
            "password_hash": hash_password(user.password),
        },
    )

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "contact": user.contact,
        "is_active": True,
    }


async def get_user_by_email(email: str):
    return await query(
        queries["user"]["get_by_email"],
        {"email": email},
    )


async def get_user_by_id(user_id: str):
    return await query(
        queries["user"]["get_by_id"],
        {"user_id": user_id},
    )


async def get_all_users():
    return await query_all(
        queries["user"]["get_all"]
    )


async def delete_user(user_id: str):
    result = await execute(
        queries["user"]["delete_user"],
        {"user_id": user_id},
    )

    return result > 0


async def login_user(email: str, password: str):
    user = await get_user_by_email(email)

    if not user:
        return None

    hashed = hash_password(password)

    if hashed != user["password_hash"]:
        return None

    token = secrets.token_hex(32)

    await execute(
        queries["user"]["update_token"],
        {"token": token, "id": user["id"]},
    )

    return {
        "id": user["id"],
        "email": user["email"],
        "token": token,
    }
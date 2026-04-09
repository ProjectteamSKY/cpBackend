import hashlib
import secrets
from app.domain.user_domain import User
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ✅ CREATE USER
async def create_user(user: User, session=None):
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


# ✅ GET USER BY EMAIL
async def get_user_by_email(email: str, session=None):
    return await query(
        queries["user"]["get_by_email"],
        {"email": email},
    )


# ✅ GET USER BY ID
async def get_user_by_id(user_id: str, session=None):
    return await query(
        queries["user"]["get_by_id"],
        {"user_id": user_id},
    )


# ✅ GET ALL USERS
async def get_all_users(session=None):
    return await query_all(queries["user"]["get_all"])


# ✅ DELETE USER
async def delete_user(user_id: str, session=None):
    result = await execute(
        queries["user"]["delete_user"],
        {"user_id": user_id},
    )
    return result > 0


# ✅ LOGIN (Bearer Token)
async def login_user(email: str, password: str):
    user = await get_user_by_email(email)

    if not user:
        return None

    hashed = hash_password(password)

    if hashed != user["password_hash"]:
        return None

    # 🔥 Generate Bearer Token
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
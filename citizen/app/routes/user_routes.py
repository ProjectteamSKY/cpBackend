# from fastapi import APIRouter, Depends, HTTPException, Form
# from pydantic import BaseModel
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.database import get_session
# from app.services import user_service
# from app.domain.user_domain import User


# from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
# from sqlalchemy.ext.asyncio import AsyncSession
# from datetime import datetime, timedelta
# import uuid
# import jwt
# import random
# from fastapi import Form

# from app.core.database import get_session
# from app.core.security import *
# from app.services.email_service import send_otp_email

# # router = APIRouter(prefix="/auth", tags=["Auth"])
# from google.oauth2 import id_token
# from google.auth.transport import requests
# from fastapi import APIRouter, HTTPException, Depends, Response
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import text
# from datetime import datetime, timedelta
# from app.core.security import create_access_token, create_refresh_token, hash_token

# GOOGLE_CLIENT_ID = "1044650935526-ihv7m03630csntjbh3sj85nn1bev4noh.apps.googleusercontent.com"

# router = APIRouter(prefix="/users", tags=["Users"])

# @router.post("/register")
# async def register(
#     full_name: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     session: AsyncSession = Depends(get_session)
# ):
#     # Check existing
#     existing = await session.execute(
#         text("SELECT id FROM users WHERE email=:email"),
#         {"email": email}
#     )
#     if existing.fetchone():
#         raise HTTPException(400, "Email already registered")

#     user_id = str(uuid.uuid4())
#     hashed = hash_password(password)

#     await session.execute(
#         text("""
#             INSERT INTO users (id, full_name, email, password_hash)
#             VALUES (:id, :name, :email, :pass)
#         """),
#         {"id": user_id, "name": full_name, "email": email, "pass": hashed}
#     )

#     otp = str(random.randint(100000, 999999))
#     expiry = datetime.utcnow() + timedelta(minutes=10)

#     await session.execute(
#         text("""
#             INSERT INTO email_otps (email, otp_code, expires_at)
#             VALUES (:email, :otp, :exp)
#         """),
#         {"email": email, "otp": otp, "exp": expiry}
#     )

#     await send_otp_email(email, otp)

#     await session.commit()

#     return {"message": "OTP sent to email"}



# @router.post("/verify-otp")
# async def verify_otp(
#     email: str = Form(...),
#     otp: str = Form(...),
#     session: AsyncSession = Depends(get_session)
# ):
#     now = datetime.utcnow()

#     result = await session.execute(
#         text("""
#             SELECT * FROM email_otps
#             WHERE email=:email 
#             AND otp_code=:otp
#             AND is_used=0 
#             AND expires_at > :now
#         """),
#         {
#             "email": email,
#             "otp": otp,
#             "now": now
#         }
#     )

#     row = result.fetchone()

#     if not row:
#         raise HTTPException(400, "Invalid or expired OTP")

#     row = row._mapping

#     await session.execute(
#         text("UPDATE users SET is_verified=1 WHERE email=:email"),
#         {"email": email}
#     )

#     await session.execute(
#         text("UPDATE email_otps SET is_used=1 WHERE id=:id"),
#         {"id": row["id"]}
#     )

#     await session.commit()

#     return {"message": "Email verified successfully"}


# @router.post("/login")
# async def login(
#     response: Response,
#     email: str = Form(...),
#     password: str = Form(...),
#     session: AsyncSession = Depends(get_session)
# ):
#     result = await session.execute(
#         text("SELECT * FROM users WHERE email=:email"),
#         {"email": email}
#     )
#     user = result.fetchone()

#     if not user:
#         raise HTTPException(401, "Invalid credentials")

#     user = user._mapping

#     if not verify_password(password, user["password_hash"]):
#         raise HTTPException(401, "Invalid credentials")

#     if not user["is_verified"]:
#         raise HTTPException(403, "Email not verified")

#     access_token = create_access_token(user["id"])
#     refresh_token = create_refresh_token(user["id"])

#     await session.execute(
#         text("""
#             INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
#             VALUES (:uid, :hash, :exp)
#         """),
#         {
#             "uid": user["id"],
#             "hash": hash_token(refresh_token),
#             "exp": datetime.utcnow() + timedelta(days=30)
#         }
#     )

#     await session.commit()

#     response.set_cookie(
#     key="access_token",
#     value=access_token,
#     httponly=True,
#     max_age=900
#     )
#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,
#         max_age=60*60*24*30
#     )

# # Return tokens in JSON (for local dev)
#     return {
#         "message": "Login successful",
#         "user_id": user["id"],
#         "access_token": access_token,
#         "refresh_token": refresh_token
#     }


# @router.post("/refresh")
# async def refresh(
#     request: Request,
#     response: Response,
#     session: AsyncSession = Depends(get_session)
# ):
#     refresh_token = request.cookies.get("refresh_token")
#     if not refresh_token:
#         raise HTTPException(401, "No refresh token")

#     try:
#         payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload["sub"]
#     except:
#         raise HTTPException(401, "Invalid token")

#     token_hash = hash_token(refresh_token)

#     result = await session.execute(
#         text("""
#             SELECT * FROM refresh_tokens
#             WHERE token_hash=:hash AND is_revoked=0
#             AND expires_at > NOW()
#         """),
#         {"hash": token_hash}
#     )

#     token_row = result.fetchone()
#     if not token_row:
#         raise HTTPException(401, "Token expired or revoked")

#     token_row = token_row._mapping

#     # Revoke old token
#     await session.execute(
#         text("UPDATE refresh_tokens SET is_revoked=1 WHERE id=:id"),
#         {"id": token_row["id"]}
#     )

#     # Create new tokens
#     new_access = create_access_token(user_id)
#     new_refresh = create_refresh_token(user_id)

#     await session.execute(
#         text("""
#             INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
#             VALUES (:uid, :hash, :exp)
#         """),
#         {
#             "uid": user_id,
#             "hash": hash_token(new_refresh),
#             "exp": datetime.utcnow() + timedelta(days=30)
#         }
#     )

#     await session.commit()

#     response.set_cookie("access_token", new_access, httponly=True, max_age=900)
#     response.set_cookie("refresh_token", new_refresh, httponly=True, max_age=60*60*24*30)

#     return {"message": "Session continued",
#             "user_id": user_id
#     }



# class GoogleLoginSchema(BaseModel):
#     token: str

# # ===================== Google Login Route =====================
# @router.post("/google-login")
# async def google_login(
#     data: GoogleLoginSchema,                 # JSON body first
#     response: Response,                       # Response injection second
#     session: AsyncSession = Depends(get_session)  # Default last
# ):
#     token = data.token  # Extract token from JSON body

#     # ---------------- Verify Google token ----------------
#     try:
#         idinfo = id_token.verify_oauth2_token(
#             token,
#             requests.Request(),
#             GOOGLE_CLIENT_ID
#         )

#         google_id = idinfo["sub"]
#         email = idinfo["email"]
#         full_name = idinfo.get("name", "")

#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid Google token")

#     # ---------------- Check if user exists ----------------
#     result = await session.execute(
#         text("SELECT * FROM users WHERE email=:email"),
#         {"email": email}
#     )
#     user = result.fetchone()

#     if user:
#         user = user._mapping
#         user_id = user["id"]
#     else:
#         # ---------------- Create new user ----------------
#         user_id = str(uuid.uuid4())
#         await session.execute(
#             text("""
#                 INSERT INTO users 
#                 (id, full_name, email, password_hash, is_verified, google_id)
#                 VALUES (:id, :name, :email, '', 1, :gid)
#             """),
#             {
#                 "id": user_id,
#                 "name": full_name,
#                 "email": email,
#                 "gid": google_id
#             }
#         )
#         await session.commit()

#     # ---------------- Create JWT tokens ----------------
#     access_token = create_access_token(user_id)
#     refresh_token = create_refresh_token(user_id)

#     # ---------------- Store refresh token ----------------
#     await session.execute(
#         text("""
#             INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
#             VALUES (:uid, :hash, :exp)
#         """),
#         {
#             "uid": user_id,
#             "hash": hash_token(refresh_token),
#             "exp": datetime.utcnow() + timedelta(days=30)
#         }
#     )
#     await session.commit()

#     # ---------------- Set cookies (HttpOnly) ----------------
#     response.set_cookie(
#     key="access_token",
#     value=access_token,
#     httponly=True,
#     max_age=900
#     )
#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,
#         max_age=60*60*24*30
#     )

# # Return tokens in JSON (for local dev)
#     return {
#         "message": "Login successful",
#         "user_id": user_id,
#         "access_token": access_token,
#         "refresh_token": refresh_token
#     }

# @router.post("/", status_code=201)
# async def create_user(
#     full_name: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     contact: str = Form(None),
#     session: AsyncSession = Depends(get_session),
# ):
#     existing = await user_service.get_user_by_email(email, session)
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already exists")

#     user = User(
#         full_name=full_name,
#         email=email,
#         password=password,
#         contact=contact,
#     )

#     return await user_service.create_user(user, session)


# @router.get("/")
# async def get_all_users():
#     return await user_service.get_all_users()


# @router.get("/{user_id}")
# async def get_user(user_id: str):
#     user = await user_service.get_user_by_id(user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# @router.delete("/{user_id}")
# async def delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
#     deleted = await user_service.delete_user(user_id, session)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"message": "User deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
import uuid
import random
import secrets

from app.core.database import get_session
from app.services.email_service import send_otp_email
from app.services import user_service
from app.domain.user_domain import User

from app.services.user_role_service import get_user_roles_by_user
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

GOOGLE_CLIENT_ID = "1044650935526-ihv7m03630csntjbh3sj85nn1bev4noh.apps.googleusercontent.com"; 


# ===================== REGISTER =====================
@router.post("/register")
async def register(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    existing = await session.execute(
        text("SELECT id FROM users WHERE email=:email"),
        {"email": email}
    )
    if existing.fetchone():
        raise HTTPException(400, "Email already registered")

    user_id = str(uuid.uuid4())
    hashed_password = user_service.hash_password(password)

    await session.execute(
        text("""
            INSERT INTO users (id, full_name, email, password_hash, is_verified)
            VALUES (:id, :name, :email, :pass, 0)
        """),
        {
            "id": user_id,
            "name": full_name,
            "email": email,
            "pass": hashed_password
        }
    )

    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)

    await session.execute(
        text("""
            INSERT INTO email_otps (email, otp_code, expires_at)
            VALUES (:email, :otp, :exp)
        """),
        {
            "email": email,
            "otp": otp,
            "exp": expiry
        }
    )

    await send_otp_email(email, otp)
    await session.commit()

    return {"message": "OTP sent to email"}


# ===================== VERIFY OTP =====================
@router.post("/verify-otp")
async def verify_otp(
    email: str = Form(...),
    otp: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    now = datetime.utcnow()

    result = await session.execute(
        text("""
            SELECT * FROM email_otps
            WHERE email=:email 
            AND otp_code=:otp
            AND is_used=0 
            AND expires_at > :now
        """),
        {"email": email, "otp": otp, "now": now}
    )

    row = result.fetchone()

    if not row:
        raise HTTPException(400, "Invalid or expired OTP")

    row = row._mapping

    await session.execute(
        text("UPDATE users SET is_verified=1 WHERE email=:email"),
        {"email": email}
    )

    await session.execute(
        text("UPDATE email_otps SET is_used=1 WHERE id=:id"),
        {"id": row["id"]}
    )

    await session.commit()

    return {"message": "Email verified successfully"}


# ===================== LOGIN (BEARER TOKEN) =====================
@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        text("SELECT * FROM users WHERE email=:email"),
        {"email": email}
    )
    user = result.fetchone()

    if not user:
        raise HTTPException(401, "Invalid credentials")

    user = user._mapping

    if user_service.hash_password(password) != user["password_hash"]:
        raise HTTPException(401, "Invalid credentials")

    if not user.get("is_verified", False):
        raise HTTPException(403, "Email not verified")

    # ✅ Fetch user roles correctly
    roles_data = await get_user_roles_by_user(user["id"])
    role_names = [role["name"] for role in roles_data]

    # 🔥 Generate Bearer Token
    bearer_token = secrets.token_hex(32)

    await session.execute(
        text("""
            UPDATE users
            SET bearer_token=:token
            WHERE id=:id
        """),
        {"token": bearer_token, "id": user["id"]}
    )

    await session.commit()

    return {
        "message": "Login successful",
        "user_id": user["id"],
        "fullname": user["full_name"],  # ✅ Include fullname
        "email": user["email"],
        "bearer_token": bearer_token,
        "roles": role_names
    }

# ===================== GOOGLE LOGIN =====================
class GoogleLoginSchema(BaseModel):
    token: str


@router.post("/google-login")
async def google_login(data: dict, session: AsyncSession = Depends(get_session)):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo.get("email")
        full_name = idinfo.get("name", "")
        if not email:
            raise ValueError("Email not found in token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    # Check if user exists
    result = await session.execute(
        text("SELECT * FROM users WHERE email=:email"),
        {"email": email}
    )
    user = result.fetchone()

    if user:
        user = user._mapping
        user_id = user["id"]
        bearer_token = user.get("bearer_token")

        # If existing user has NO token, generate it
        if not bearer_token:
            bearer_token = secrets.token_hex(32)
            await session.execute(
                text("UPDATE users SET bearer_token=:token WHERE id=:id"),
                {"token": bearer_token, "id": user_id}
            )
            await session.commit()

    else:
        # New user: create and generate token
        user_id = str(uuid.uuid4())
        bearer_token = secrets.token_hex(32)
        await session.execute(
            text("""
                INSERT INTO users (id, full_name, email, password_hash, is_verified, bearer_token)
                VALUES (:id, :name, :email, '', 1, :token)
            """),
            {"id": user_id, "name": full_name, "email": email, "token": bearer_token}
        )
        await session.commit()

    # Fetch roles
    roles_data = await get_user_roles_by_user(user_id)
    role_names = [role["name"] for role in roles_data]

    return {
        "message": "Login successful",
        "user_id": user_id,
        "bearer_token": bearer_token,
        "roles": role_names
    }
# ===================== CREATE USER =====================
@router.post("/", status_code=201)
async def create_user(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    contact: str = Form(None),
):
    existing = await user_service.get_user_by_email(email)

    if existing:
        raise HTTPException(400, "Email already exists")

    user = User(
        full_name=full_name,
        email=email,
        password=password,
        contact=contact,
    )

    return await user_service.create_user(user)


# ===================== GET ALL USERS =====================
@router.get("/")
async def get_all_users():
    return await user_service.get_all_users()


# ===================== GET USER =====================
@router.get("/{user_id}")
async def get_user(user_id: str):
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user


# ===================== DELETE USER =====================
@router.delete("/{user_id}")
async def delete_user(user_id: str):
    deleted = await user_service.delete_user(user_id)

    if not deleted:
        raise HTTPException(404, "User not found")

    return {"message": "User deleted successfully"}
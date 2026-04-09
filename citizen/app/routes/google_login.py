from fastapi import APIRouter, HTTPException, Form
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.database import execute
from app.services import user_service
from app.services.user_role_service import assign_role_service, get_roles_by_user_service
from app.services.otpservice import generate_otp, send_otp_email, verify_otp
import secrets

router = APIRouter()

GOOGLE_CLIENT_ID = "1044650935526-ihv7m03630csntjbh3sj85nn1bev4noh.apps.googleusercontent.com"


class AssignRolePayload:
    def __init__(self, user_id, role_id, assigned_by):
        self.user_id = user_id
        self.role_id = role_id
        self.assigned_by = assigned_by


@router.post("/auth/google")
async def google_login(payload: dict):
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = idinfo["email"]
    name = idinfo.get("name", "")

    user = await user_service.get_user_by_email(email)
    if not user:
        user = await user_service.create_google_user(name, email)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        await assign_role_service(
            AssignRolePayload(user_id=user["id"], role_id=1, assigned_by=user["id"])
        )

    roles_data = await get_roles_by_user_service(user["id"])
    role_names = [role["name"] for role in roles_data]

    bearer_token = secrets.token_hex(32)
    await execute(
        'UPDATE "User" SET bearer_token = $1 WHERE id = $2',
        [bearer_token, user["id"]],
    )

    return {
        "token": bearer_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "roles": role_names,
        },
    }


@router.post("/auth/send-otp")
async def send_otp(payload: dict):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email missing")

    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="No account found with that email")

    otp = generate_otp(email)
    send_otp_email(email, otp)

    return {"status": "otp_sent", "email": email}


@router.post("/auth/verify-otp")
async def verify_otp_route(
    email: str = Form(...),
    otp: str = Form(...),
):
    if not verify_otp(email, otp):
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    roles_data = await get_roles_by_user_service(user["id"])
    role_names = [role["name"] for role in roles_data]

    bearer_token = secrets.token_hex(32)
    await execute(
        'UPDATE "User" SET bearer_token = $1 WHERE id = $2',
        [bearer_token, user["id"]],
    )

    return {
        "token": bearer_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "roles": role_names,
        },
    }


@router.post("/auth/resend-otp")
async def resend_otp(payload: dict):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email missing")

    otp = generate_otp(email)
    send_otp_email(email, otp)

    return {"status": "otp_sent", "email": email}
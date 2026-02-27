from fastapi import APIRouter, Depends, HTTPException, Form
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.password_token_domain import PasswordResetToken
from app.services.password_token_service import password_token_service
import secrets

router = APIRouter(prefix="/password-reset", tags=["Password Reset"])


@router.post("/request")
async def request_reset(
    user_id: int = Form(...),
    session: AsyncSession = Depends(get_session),
):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    token_obj = PasswordResetToken(user_id, token, expires_at)
    return await password_token_service.create_token(token_obj, session)


@router.post("/confirm")
async def confirm_reset(
    token: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    token_data = await password_token_service.get_token(token, session)

    if not token_data:
        raise HTTPException(status_code=404, detail="Invalid token")

    if token_data["used"]:
        raise HTTPException(status_code=400, detail="Token already used")

    if token_data["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    await password_token_service.mark_token_used(token, session)
    return {"message": "Token validated"}

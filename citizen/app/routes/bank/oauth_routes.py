from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.bank_services.oauth_service import (
    generate_access_token,
    get_valid_access_token
)

router = APIRouter()


# OAuth Callback from Bank
# OAuth callback from bank
@router.get("/oauth-callback")
async def oauth_callback(
    code: str,
    scope: Optional[str] = "upi",
    state: Optional[str] = None
):

    try:
        token = await generate_access_token(code, scope)

        return {
            "message": "Access token generated",
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get valid access token
@router.get("/access-token")
async def get_access_token():

    try:
        token = await get_valid_access_token()

        return {
            "access_token": token
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


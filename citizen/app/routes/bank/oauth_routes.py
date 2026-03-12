from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.bank_services.oauth_service import (
    generate_access_token,
    refresh_access_token,
    get_saved_access_token,
    get_saved_refresh_token
)

router = APIRouter()


# ---------------------------------------
# OAuth Redirect Callback
# ---------------------------------------
@router.get("/oauth-callback")
async def oauth_callback(code: str, scope: str = None, state: str = None):

    try:
        token_data = await generate_access_token(code, scope)

        return {
            "message": "Access token generated successfully",
            "code": code,
            "scope": scope,
            "state": state,
            "token_data": token_data
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------
# Refresh Token API
# ---------------------------------------
@router.post("/refresh-token")
async def refresh_token():

    refresh_token_value = get_saved_refresh_token()

    if not refresh_token_value:
        raise HTTPException(status_code=400, detail="No refresh token available")

    try:
        token_data = await refresh_access_token(refresh_token_value)

        return {
            "message": "Token refreshed successfully",
            "data": token_data
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------
# Get Access Token
# ---------------------------------------
@router.get("/access-token")
async def get_access_token():

    token = get_saved_access_token()

    if not token:
        raise HTTPException(status_code=404, detail="No token found")

    return {"access_token": token}

# @router.post("/upi-callback")
# async def upi_callback(request: Request):
#     """
#     Handle UPI payment callback from Canara Bank
#     """

#     try:
#         payload = await request.json()
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid JSON payload")

#     txn_id = payload.get("transactionId") or "unknown_txn"

#     upi_responses[txn_id] = payload

#     return JSONResponse(
#         content={
#             "message": "UPI callback received",
#             "transactionId": txn_id,
#             "status": payload.get("status")
#         }
#     )
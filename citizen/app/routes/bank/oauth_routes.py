from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from app.services.bank_services.oauth_service import (
  generate_access_token, refresh_access_token, get_saved_access_token
)

router = APIRouter()



router = APIRouter()

@router.post("/generate-token")
async def generate_token(code: str = Query(..., description="Authorization code from step 1")):
    try:
        token_data = await generate_access_token(code)
        return {"message": "Access token generated successfully", "data": token_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh-token")
async def refresh_token():
    refresh_token = get_saved_access_token()  # or get refresh token separately
    if not refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token available. Generate access token first.")
    try:
        token_data = await refresh_access_token(refresh_token)
        return {"message": "Token refreshed successfully", "data": token_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


oauth_tokens = {}
upi_responses = {}

@router.get("/access-token")
async def get_token():
    token = get_saved_access_token()
    if not token:
        raise HTTPException(status_code=404, detail="No access token found")
    return {"access_token": token}


@router.get("/api/bank/oauth-callback")
async def oauth_callback(code: str):
    return {"message": "OAuth code received", "code": code}


@router.post("/upi-callback")
async def upi_callback(request: Request):
    """
    Handle UPI payment callback from Canara Bank.
    Receives payment status, transaction id, and other details.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Store UPI callback data for demo purposes
    txn_id = payload.get("transactionId") or "unknown_txn"
    upi_responses[txn_id] = payload

    # You can also process the payment status here (success/failure)
    return JSONResponse(content={"message": "UPI callback received", "transactionId": txn_id, "status": payload.get("status")})
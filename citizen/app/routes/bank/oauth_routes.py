from fastapi import APIRouter, HTTPException, Query
from app.services.bank_services.oauth_service import (
  generate_access_token, refresh_access_token, get_saved_access_token
)

router = APIRouter()



router = APIRouter(prefix="/canara", tags=["Canara Bank"])

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


@router.get("/access-token")
async def get_token():
    token = get_saved_access_token()
    if not token:
        raise HTTPException(status_code=404, detail="No access token found")
    return {"access_token": token}
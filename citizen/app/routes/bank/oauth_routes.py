# from fastapi import APIRouter, HTTPException, Query
# from typing import Optional

# from app.services.bank_services.oauth_service import (
#     generate_access_token,
#     refresh_access_token,
#     get_access_token,
#     get_refresh_token
# )
# import logging

# logger = logging.getLogger("oauth_logger")
# logging.basicConfig(level=logging.INFO)
# router = APIRouter()


# # OAuth Callback from Bank
# @router.get("/oauth-callback")
# async def oauth_callback(code: str, scope: Optional[str] = "upi", state: Optional[str] = None):
#     logger.info("code: %s", code)
#     logger.info("scope: %s", scope)
#     logger.info("state: %s", state)

#     try:
#         token = await generate_access_token(code, scope)
#         logger.info("Access token generated successfully")
#         return {
#             "message": "Access token generated successfully",
#             "access_token": token.get("access_token"),
#             "refresh_token": token.get("refresh_token")
#         }
#     except Exception as e:
#         logger.error("Error generating token: %s", e)
#         raise HTTPException(status_code=400, detail=str(e))


# # Manual Token Generation
# @router.post("/generate-token")
# async def manual_generate_token(
#     code: str = Query(...),
#     scope: str = Query("van")
# ):

#     try:
#         token = await generate_access_token(code, scope)

#         return {
#             "message": "Token generated",
#             "data": token
#         }

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # Refresh Access Token
# @router.post("/refresh-token")
# async def refresh_token():

#     refresh_token_value = get_refresh_token()

#     if not refresh_token_value:
#         raise HTTPException(status_code=400, detail="Refresh token not available")

#     try:
#         token = await refresh_access_token(refresh_token_value)

#         return {
#             "message": "Access token refreshed",
#             "data": token
#         }

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# # Get Current Access Token
# @router.get("/access-token")
# def current_access_token():

#     token = get_access_token()
#     print("token - oauth_routes.py:82",token)
#     if not token:
#         raise HTTPException(status_code=404, detail="Access token not found")

#     return {"access_token": token}


from fastapi import APIRouter, HTTPException

from app.services.bank_services.oauth_service import (
    generate_access_token,
    get_valid_access_token
)

router = APIRouter()


@router.get("/oauth-callback")
async def oauth_callback(code: str):
    try:
        data = await generate_access_token(code)

        return {
            "message": "Token generated",
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ✅ GET TOKEN
@router.get("/access-token")
async def get_token():
    try:
        token = await get_valid_access_token()

        return {"access_token": token}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
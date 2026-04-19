from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from datetime import date

from app.domain.user_profile_domain import UserProfile
from app.services import user_profile_service

# ❌ NO prefix here (already added in main router)
router = APIRouter()


# ✅ CREATE PROFILE (REST style)
@router.post("/")
async def create_profile(
    user_id: str = Form(...),
    profile_picture: str = Form(None),
    phone_number: str = Form(None),
    gender: str = Form("Not Specified"),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    country: str = Form(None),
    postal_code: str = Form(None),
    date_of_birth: str = Form(None),
):
    from datetime import datetime

    dob = None
    if date_of_birth:
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except:
            raise HTTPException(400, "Invalid date format")

    profile = UserProfile(
        user_id=user_id,
        profile_picture=profile_picture,
        phone_number=phone_number,
        gender=gender,
        address=address,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code,
        date_of_birth=dob,
    )

    # 🔥 KEY FIX HERE
    existing = await user_profile_service.get_profile(user_id)

    if existing:
        return await user_profile_service.update_profile(profile)
    else:
        return await user_profile_service.create_profile(profile)


# ✅ GET PROFILE (AUTO CREATE FIX)
@router.get("/{user_id}")
async def get_profile(user_id: str):
    profile = await user_profile_service.get_profile(user_id)

    # 🔥 AUTO CREATE instead of 404
    if not profile:
        await user_profile_service.create_profile(
            UserProfile(
                user_id=user_id,
                gender="Not Specified"
            )
        )

        profile = await user_profile_service.get_profile(user_id)

    return profile


# ✅ UPDATE PROFILE
@router.put("/{user_id}")
async def update_profile(
    user_id: str,
    profile_picture: str = Form(None),
    phone_number: str = Form(None),
    gender: str = Form("Not Specified"),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    country: str = Form(None),
    postal_code: str = Form(None),
    date_of_birth: date = Form(None),
):
    profile = UserProfile(
        user_id=user_id,
        profile_picture=profile_picture,
        phone_number=phone_number,
        gender=gender,
        address=address,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code,
        date_of_birth=date_of_birth,
    )

    return await user_profile_service.update_profile(profile)


# ✅ DELETE PROFILE
@router.delete("/{user_id}")
async def delete_profile(user_id: str):
    deleted = await user_profile_service.delete_profile(user_id)

    if not deleted:
        raise HTTPException(404, "Profile not found")

    return {"message": "Profile deleted successfully"}

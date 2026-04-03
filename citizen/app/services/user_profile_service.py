from sqlalchemy.exc import IntegrityError  # ✅ FIXED

from app.utils.query_loader import load_queries
from app.core.database import execute, query

queries = load_queries()


async def create_profile(profile):
    try:
        # ✅ TRY INSERT
        await execute(
            queries["user_profile"]["create_profile"],
            profile.__dict__,
        )
        return {"message": "Profile created successfully"}

    except IntegrityError:
        # ✅ IF EXISTS → UPDATE
        await execute(
            queries["user_profile"]["update_profile"],
            profile.__dict__,
        )
        return {"message": "Profile updated successfully"}


async def get_profile(user_id: str):
    profile = await query(
        queries["user_profile"]["get_profile"],
        {"user_id": user_id},
    )

    if not profile:
        # ✅ AUTO CREATE PROFILE
        await execute(
            queries["user_profile"]["create_profile"],
            {
                "user_id": user_id,
                "profile_picture": None,
                "phone_number": None,
                "gender": "Not Specified",
                "address": None,
                "city": None,
                "state": None,
                "country": None,
                "postal_code": None,
                "date_of_birth": None,
            },
        )

        # fetch again
        profile = await query(
            queries["user_profile"]["get_profile"],
            {"user_id": user_id},
        )

    return profile

async def update_profile(profile):
    await execute(
        queries["user_profile"]["update_profile"],
        {
            "user_id": profile.user_id,
            "profile_picture": profile.profile_picture,
            "phone_number": profile.phone_number,
            "gender": profile.gender,
            "address": profile.address,
            "city": profile.city,
            "state": profile.state,
            "country": profile.country,
            "postal_code": profile.postal_code,
            "date_of_birth": profile.date_of_birth,
        },
    )

    return {"message": "Profile updated successfully"}


async def delete_profile(user_id: str):
    result = await execute(
        queries["user_profile"]["delete_profile"],
        {"user_id": user_id},
    )

    return result > 0
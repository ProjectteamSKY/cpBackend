from app.utils.query_loader import load_queries
from app.core.database import execute, query

queries = load_queries()


# =========================================================
# CREATE PROFILE
# =========================================================
async def create_profile(profile):

    await execute(
        queries["user_profile"]["create_profile"],
        {
            "user_id": profile.user_id,
            "profile_picture": profile.profile_picture,
            "phone_number": profile.phone_number,
            "gender": profile.gender,
            "date_of_birth": profile.date_of_birth,
        },
    )

    return True


# =========================================================
# GET PROFILE
# =========================================================
async def get_profile(user_id: str):

    profile = await query(
        queries["user_profile"]["get_profile"],
        {
            "user_id": user_id,
        },
    )

    return profile


# =========================================================
# UPDATE PROFILE
# =========================================================
async def update_profile(profile):

    await execute(
        queries["user_profile"]["update_profile"],
        {
            "user_id": profile.user_id,
            "profile_picture": profile.profile_picture,
            "phone_number": profile.phone_number,
            "gender": profile.gender,
            "date_of_birth": profile.date_of_birth,
        },
    )

    updated_profile = await get_profile(
        profile.user_id
    )

    return updated_profile


# =========================================================
# DELETE PROFILE
# =========================================================
async def delete_profile(user_id: str):

    result = await execute(
        queries["user_profile"]["delete_profile"],
        {
            "user_id": user_id,
        },
    )

    return result > 0
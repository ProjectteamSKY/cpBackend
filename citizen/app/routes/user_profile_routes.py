from fastapi import (
    APIRouter,
    HTTPException,
    Form,
    UploadFile,
    File,
)

from datetime import datetime
from pathlib import Path
from PIL import Image
import shutil
import uuid
import os

from app.domain.user_profile_domain import UserProfile
from app.services import user_profile_service

router = APIRouter()


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

UPLOAD_DIR = BASE_DIR / "media" / "profile_pictures"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# IMAGE COMPRESS FUNCTION
# =========================================================

def compress_image(
    input_path,
    output_path,
    quality=70,
    max_size=(800, 800),
):

    image = Image.open(input_path)

    # RGB convert for JPG save
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # Resize
    image.thumbnail(max_size)

    # Save compressed
    image.save(
        output_path,
        optimize=True,
        quality=quality
    )


# =========================================================
# CREATE PROFILE
# =========================================================
@router.post("/")
async def create_profile(
    user_id: str = Form(...),

    profile_picture: UploadFile | None = File(None),

    phone_number: str | None = Form(None),

    gender: str = Form("Not Specified"),

    date_of_birth: str | None = Form(None),
):

    # =====================================================
    # CHECK EXISTING PROFILE
    # =====================================================

    existing = await user_profile_service.get_profile(
        user_id
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    # =====================================================
    # DATE PARSE
    # =====================================================

    dob = None

    if date_of_birth:
        try:
            dob = datetime.strptime(
                date_of_birth,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    # =====================================================
    # IMAGE UPLOAD + COMPRESS
    # =====================================================

    image_path = None

    if profile_picture:

        allowed_extensions = [
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]

        extension = (
            profile_picture.filename
            .split(".")[-1]
            .lower()
        )

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG, WEBP allowed"
            )

        file_name = (
            f"{uuid.uuid4()}.jpg"
        )

        temp_path = (
            UPLOAD_DIR /
            f"temp_{file_name}"
        )

        final_path = (
            UPLOAD_DIR / file_name
        )

        # Save temp
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(
                profile_picture.file,
                buffer
            )

        # Compress
        compress_image(
            temp_path,
            final_path,
            quality=70,
            max_size=(800, 800)
        )

        # Delete temp file
        os.remove(temp_path)

        # Save DB path
        image_path = (
            f"/media/profile_pictures/{file_name}"
        )

    # =====================================================
    # CREATE MODEL
    # =====================================================

    profile = UserProfile(
        user_id=user_id,

        profile_picture=image_path,

        phone_number=phone_number,

        gender=gender,

        date_of_birth=dob,
    )

    await user_profile_service.create_profile(
        profile
    )

    created = await user_profile_service.get_profile(
        user_id
    )

    return {
        "message": "Profile created successfully",
        "data": created
    }


# =========================================================
# GET PROFILE
# =========================================================
@router.get("/{user_id}")
async def get_profile(user_id: str):

    profile = await user_profile_service.get_profile(
        user_id
    )

    if not profile:

        empty_profile = UserProfile(
            user_id=user_id
        )

        await user_profile_service.create_profile(
            empty_profile
        )

        profile = await user_profile_service.get_profile(
            user_id
        )

    return profile


# =========================================================
# UPDATE PROFILE
# =========================================================
@router.put("/{user_id}")
async def update_profile(
    user_id: str,

    profile_picture: UploadFile | None = File(None),

    phone_number: str | None = Form(None),

    gender: str = Form("Not Specified"),

    date_of_birth: str | None = Form(None),
):

    # =====================================================
    # CHECK PROFILE
    # =====================================================

    existing = await user_profile_service.get_profile(
        user_id
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    # =====================================================
    # DATE PARSE
    # =====================================================

    dob = existing.get(
        "date_of_birth"
    )

    if date_of_birth:
        try:
            dob = datetime.strptime(
                date_of_birth,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    # =====================================================
    # IMAGE PROCESS
    # =====================================================

    image_path = existing.get(
        "profile_picture"
    )

    if profile_picture:

        allowed_extensions = [
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]

        extension = (
            profile_picture.filename
            .split(".")[-1]
            .lower()
        )

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG, WEBP allowed"
            )

        file_name = (
            f"{uuid.uuid4()}.jpg"
        )

        temp_path = (
            UPLOAD_DIR /
            f"temp_{file_name}"
        )

        final_path = (
            UPLOAD_DIR / file_name
        )

        # Save temp
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(
                profile_picture.file,
                buffer
            )

        # Compress image
        compress_image(
            temp_path,
            final_path,
            quality=70,
            max_size=(800, 800)
        )

        # Delete temp
        os.remove(temp_path)

        # Delete old image
        old_image = existing.get(
            "profile_picture"
        )

        if old_image:

            old_path = (
                BASE_DIR /
                old_image.lstrip("/")
            )

            if old_path.exists():
                old_path.unlink()

        image_path = (
            f"/media/profile_pictures/{file_name}"
        )

    # =====================================================
    # UPDATE MODEL
    # =====================================================

    profile = UserProfile(
        user_id=user_id,

        profile_picture=image_path,

        phone_number=(
            phone_number
            if phone_number is not None
            else existing.get("phone_number")
        ),

        gender=(
            gender
            if gender is not None
            else existing.get("gender")
        ),

        date_of_birth=dob,
    )

    updated = await user_profile_service.update_profile(
        profile
    )

    return {
        "message": "Profile updated successfully",
        "data": updated
    }


# =========================================================
# DELETE PROFILE
# =========================================================
@router.delete("/{user_id}")
async def delete_profile(user_id: str):

    existing = await user_profile_service.get_profile(
        user_id
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    # =====================================================
    # DELETE IMAGE
    # =====================================================

    old_image = existing.get(
        "profile_picture"
    )

    if old_image:

        old_path = (
            BASE_DIR /
            old_image.lstrip("/")
        )

        if old_path.exists():
            old_path.unlink()

    # =====================================================
    # DELETE DB
    # =====================================================

    await user_profile_service.delete_profile(
        user_id
    )

    return {
        "message": "Profile deleted successfully"
    }
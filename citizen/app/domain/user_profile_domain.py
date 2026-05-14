from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserProfile(BaseModel):

    user_id: str

    profile_picture: Optional[str] = None
    phone_number: Optional[str] = None

    gender: Optional[str] = "Not Specified"

    date_of_birth: Optional[date] = None
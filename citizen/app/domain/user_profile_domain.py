from typing import Optional
from datetime import datetime, date


class UserProfile:
    def __init__(
        self,
        user_id: str,
        profile_picture: Optional[str] = None,
        phone_number: Optional[str] = None,
        gender: Optional[str] = "Not Specified",
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.profile_picture = profile_picture
        self.phone_number = phone_number
        self.gender = gender
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.date_of_birth = date_of_birth
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
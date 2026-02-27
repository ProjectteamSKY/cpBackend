from typing import Optional, Dict
from datetime import date, datetime

class User_Profile:
    def __init__(
        self,
        user_id: int,
        profile_picture: Optional[str] = None,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        bio: Optional[str] = None,
        timezone: Optional[str] = None,
        notification_preferences: Optional[Dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.profile_picture = profile_picture
        self.phone_number = phone_number
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.date_of_birth = date_of_birth
        self.bio = bio
        self.timezone = timezone
        self.notification_preferences = notification_preferences
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
from datetime import datetime


class PasswordResetToken:
    def __init__(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
        used: bool = False,
        created_at: datetime = None,
    ):
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.used = used
        self.created_at = created_at or datetime.utcnow()

import uuid
from datetime import datetime


class ContactRequest:

    def __init__(
        self,
        full_name: str,
        phone_number: str,
        email_address: str,
        subject: str,
        message: str,
        status: str = "new",
        id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())

        self.full_name = full_name
        self.phone_number = phone_number
        self.email_address = email_address
        self.subject = subject
        self.message = message
        self.status = status

        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "email_address": self.email_address,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
        }
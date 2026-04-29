from datetime import datetime, timezone
from typing import Optional


class Transaction:

    def __init__(
        self,
        ext_transaction_id: str,
        amount: float,
        order_id: Optional[str] = None,
        status: str = "PENDING",
        qr_string: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        paid_at: Optional[datetime] = None
    ):
        self.id = id
        self.order_id = order_id
        self.ext_transaction_id = ext_transaction_id
        self.amount = amount
        self.status = status
        self.qr_string = qr_string

        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.paid_at = paid_at

    # ------------------------
    # Status Methods
    # ------------------------

    def mark_success(self):
        self.status = "SUCCESS"
        self.paid_at = datetime.now(timezone.utc)
        self.touch()

    def mark_failed(self):
        self.status = "FAILED"
        self.touch()

    def mark_pending(self):
        self.status = "PENDING"
        self.touch()

    # ------------------------
    # Order Linking
    # ------------------------

    def attach_order(self, order_id: str):
        self.order_id = order_id
        self.touch()

    # ------------------------
    # Update Helpers
    # ------------------------

    def update_amount(self, amount: float):
        self.amount = amount
        self.touch()

    def update_qr(self, qr_string: str):
        self.qr_string = qr_string
        self.touch()

    def touch(self):
        self.updated_at = datetime.now(timezone.utc)

    # ------------------------
    # DB Payload Methods
    # ------------------------

    def to_insert_dict(self):
        """
        Use this for INSERT query
        (No id, DB auto-generates)
        """
        return {
            "order_id": self.order_id,
            "ext_transaction_id": self.ext_transaction_id,
            "amount": self.amount,
            "status": self.status,
            "qr_string": self.qr_string,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_update_dict(self):
        """
        Use this for UPDATE query
        """
        return {
            "order_id": self.order_id,
            "amount": self.amount,
            "status": self.status,
            "qr_string": self.qr_string,
            "updated_at": self.updated_at,
        }

    # ------------------------
    # Response / Output
    # ------------------------

    def to_dict(self):
        """
        Full response (API output)
        """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "ext_transaction_id": self.ext_transaction_id,
            "amount": self.amount,
            "status": self.status,
            "qr_string": self.qr_string,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "paid_at": self.paid_at,
        }
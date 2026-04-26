import uuid
from datetime import datetime
from typing import Optional


class Order:
    def __init__(
        self,
        user_id: str,
        cart_id: str,
        total_amount: float,
        payment_method: str,

        # Optional / Extended fields
        address_id: Optional[str] = None,
        order_number: Optional[str] = None,

        delivery_charge: float = 0,
        courier_id: Optional[str] = None,
        courier_name: Optional[str] = None,
        estimated_delivery_date: Optional[datetime] = None,

        delivery_type: str = "normal",

        payment_status: str = "pending",
        status: str = "pending",

        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        # Core IDs
        self.id: str = id or str(uuid.uuid4())
        self.order_number: Optional[str] = order_number

        # Relations
        self.user_id: str = user_id
        self.cart_id: str = cart_id
        self.address_id: Optional[str] = address_id

        # Delivery / Courier
        self.delivery_charge: float = delivery_charge
        self.courier_id: Optional[str] = courier_id
        self.courier_name: Optional[str] = courier_name
        self.estimated_delivery_date: Optional[datetime] = estimated_delivery_date
        self.delivery_type: str = delivery_type

        # Payment
        self.payment_method: str = payment_method
        self.payment_status: str = payment_status

        # Order state
        self.status: str = status

        # Amount
        self.total_amount: float = total_amount

        # Timestamps
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # -------------------------
    # Convert to dictionary (API response)
    # -------------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_number": self.order_number,

            "user_id": self.user_id,
            "cart_id": self.cart_id,
            "address_id": self.address_id,

            "delivery_charge": float(self.delivery_charge or 0),
            "courier_id": self.courier_id,
            "courier_name": self.courier_name,
            "estimated_delivery_date": (
                self.estimated_delivery_date.isoformat()
                if isinstance(self.estimated_delivery_date, datetime)
                else self.estimated_delivery_date
            ),

            "delivery_type": self.delivery_type,

            "payment_method": self.payment_method,
            "payment_status": self.payment_status,

            "status": self.status,
            "total_amount": float(self.total_amount),

            "created_at": self.created_at.isoformat()
            if isinstance(self.created_at, datetime)
            else self.created_at,

            "updated_at": self.updated_at.isoformat()
            if isinstance(self.updated_at, datetime)
            else self.updated_at,
        }

    # -------------------------
    # Create object from DB row
    # -------------------------
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            order_number=data.get("order_number"),

            user_id=data["user_id"],
            cart_id=data["cart_id"],
            address_id=data.get("address_id"),

            delivery_charge=float(data.get("delivery_charge", 0)),
            courier_id=data.get("courier_id"),
            courier_name=data.get("courier_name"),
            estimated_delivery_date=data.get("estimated_delivery_date"),

            delivery_type=data.get("delivery_type", "normal"),

            payment_method=data.get("payment_method", "COD"),
            payment_status=data.get("payment_status", "pending"),

            status=data.get("status", "pending"),
            total_amount=float(data["total_amount"]),

            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
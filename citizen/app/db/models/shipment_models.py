import uuid
from datetime import datetime
from sqlalchemy import Column, Enum, Float, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

import enum

class ShipmentStatus(str, enum.Enum):
    pending = "pending"
    shipped = "shipped"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"
    returned = "returned"
    canceled = "canceled"

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to the order
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    # ShipRocket specific
    shiprocket_order_id = Column(String(100), unique=True, nullable=False)  # ShipRocket internal ID
    tracking_number = Column(String(100), unique=True, nullable=False)       # Courier tracking number

    # Courier info
    courier_name = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=True)                          # express, standard
    shipping_cost = Column(Float, nullable=True)

    # Shipment status & attempts
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.pending, nullable=False)
    delivery_attempts = Column(Integer, default=0, nullable=False)
    delivery_notes = Column(Text, nullable=True)                              # Reason for failed delivery
    api_response = Column(Text, nullable=True)                                # Last API response from ShipRocket

    # Important dates
    shipped_at = Column(DateTime, nullable=True)
    expected_delivery = Column(DateTime, nullable=True)                       # Show to user
    delivered_at = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)

    # Retry / contact logic
    is_retry_allowed = Column(Boolean, default=True)
    last_contacted_at = Column(DateTime, nullable=True)

    # Record timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to order
    order = relationship("Order", back_populates="shipment")

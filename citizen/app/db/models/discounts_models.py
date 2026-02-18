import uuid
from datetime import datetime
from sqlalchemy import Column, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    description = Column(Text)
    discount_type = Column(String(20), default="percentage")  # "percentage" or "fixed"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="discount")
    product = relationship("Product", back_populates="discounts")


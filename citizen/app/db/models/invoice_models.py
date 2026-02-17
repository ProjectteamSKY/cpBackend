import uuid
from datetime import datetime
from sqlalchemy import Column, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"))
    invoice_number = Column(String(100), unique=True, nullable=False)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    gst_amount = Column(Float, nullable=False)
    final_amount = Column(Float, nullable=False)
    pdf_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="invoice")
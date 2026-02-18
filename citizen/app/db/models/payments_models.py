import uuid
from datetime import datetime
from sqlalchemy import Column, Float, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


# =========================
# Payment
# =========================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    payment_number = Column(String(100), unique=True, nullable=False)
    transaction_id = Column(String(255), index=True)

    payment_method = Column(String(50), nullable=False)  # card, upi, cod, netbanking
    payment_gateway = Column(String(50))  # razorpay, stripe, paytm

    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")

    status = Column(String(50), default="pending")  
    # pending, success, failed, refunded

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="payments")
    refunds = relationship("Refund", back_populates="payment")


# =========================
# Refund
# =========================
class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"))

    refund_amount = Column(Float, nullable=False)
    refund_status = Column(String(50), default="pending")

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    payment = relationship("Payment", back_populates="refunds")


# =========================
# Payment Method
# =========================
class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    method_type = Column(String(50))  # card, upi, bank

    provider = Column(String(50))  # visa, razorpay, paytm

    last_four = Column(String(4))

    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("User")


# =========================
# Bank Account
# =========================
class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    account_holder_name = Column(String(200))
    account_number = Column(String(255))
    ifsc_code = Column(String(50))

    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("User")


# =========================
# Payout
# =========================
class Payout(Base):
    __tablename__ = "payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    payout_number = Column(String(100), unique=True, nullable=False)

    amount = Column(Float, nullable=False)

    status = Column(String(50), default="pending")
    # pending, completed, failed

    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("User")

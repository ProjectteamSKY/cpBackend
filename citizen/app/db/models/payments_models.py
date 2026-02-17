import uuid
from datetime import datetime
from sqlalchemy import JSON, Column, Float, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

# class Payment(Base):
#     __tablename__ = "payments"

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"))
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
#     amount = Column(Float, nullable=False)
#     payment_method = Column(String(50))  # HDFC, Canara Bank, UPI
#     status = Column(String(50), default="pending")  # pending, completed, failed
#     transaction_id = Column(String(100), unique=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     order = relationship("Order")
#     user = relationship("User", back_populates="payments")



class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    # Payment identification
    payment_number = Column(String(100), unique=True, nullable=False)
    transaction_id = Column(String(500), index=True)
    payment_id = Column(String(500), index=True)  # Gateway payment ID
    
    # Payment details
    payment_method = Column(String(50), nullable=False)  # card, upi, netbanking, wallet, cod, bank_transfer
    payment_gateway = Column(String(50))  # razorpay, paytm, stripe, direct_bank
    payment_type = Column(String(50))  # prepaid, cod, partial
    
    # Amounts
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    gateway_fee = Column(Float, default=0)
    gateway_tax = Column(Float, default=0)
    net_amount = Column(Float)  # amount - gateway_fee - gateway_tax
    
    # Currency
    currency = Column(String(10), default="INR")
    
    # Status
    status = Column(String(50), default="pending", index=True)  # pending, initiated, authorized, captured, failed, refunded, partially_refunded
    
    # Gateway response
    gateway_response = Column(JSON)
    gateway_request = Column(JSON)
    
    # Bank transfer specific
    bank_name = Column(String(200))
    account_number = Column(String(100))
    ifsc_code = Column(String(50))
    account_holder_name = Column(String(200))
    transaction_reference = Column(String(500))
    utr_number = Column(String(500))
    
    # UPI specific
    upi_id = Column(String(200))
    upi_transaction_id = Column(String(500))
    
    # Card specific
    card_last_four = Column(String(4))
    card_network = Column(String(50))
    card_type = Column(String(50))  # credit, debit
    
    # Refund details
    refund_amount = Column(Float, default=0)
    refund_status = Column(String(50))
    refund_transaction_id = Column(String(500))
    refund_initiated_at = Column(DateTime)
    refund_completed_at = Column(DateTime)
    
    # Timestamps
    initiated_at = Column(DateTime, default=datetime.utcnow)
    authorized_at = Column(DateTime)
    captured_at = Column(DateTime)
    failed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="payments")
    refunds = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")
    logs = relationship("PaymentLog", back_populates="payment", cascade="all, delete-orphan")

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"))
    
    # Refund identification
    refund_number = Column(String(100), unique=True, nullable=False)
    transaction_id = Column(String(500), index=True)
    gateway_refund_id = Column(String(500))
    
    # Refund details
    refund_type = Column(String(50))  # full, partial
    refund_method = Column(String(50))  # original, wallet, bank_transfer, store_credit
    reason = Column(String(500))
    notes = Column(Text)
    
    # Amounts
    amount = Column(Float, nullable=False)
    gateway_fee_refunded = Column(Float, default=0)
    
    # Items refunded
    items = Column(JSON)  # List of items and quantities refunded
    
    # Status
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed, rejected
    
    # Gateway response
    gateway_response = Column(JSON)
    
    # Bank details (if bank transfer)
    bank_name = Column(String(200))
    account_number = Column(String(100))
    ifsc_code = Column(String(50))
    account_holder_name = Column(String(200))
    transaction_reference = Column(String(500))
    utr_number = Column(String(500))
    
    # Timestamps
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="refunds")
    payment = relationship("Payment", back_populates="refunds")



class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    method_type = Column(String(50))  # card, bank_account, upi, wallet
    is_default = Column(Boolean, default=False)
    
    # Card details (encrypted)
    card_token = Column(String(500))
    card_last_four = Column(String(4))
    card_network = Column(String(50))
    card_holder_name = Column(String(200))
    card_expiry_month = Column(String(2))
    card_expiry_year = Column(String(4))
    
    # Bank account details (encrypted)
    bank_account_token = Column(String(500))
    account_holder_name = Column(String(200))
    account_number_last_four = Column(String(4))
    ifsc_code = Column(String(50))
    bank_name = Column(String(200))
    
    # UPI details
    upi_id = Column(String(200))
    
    # Wallet details
    wallet_provider = Column(String(50))
    wallet_balance = Column(Float, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    account_holder_name = Column(String(200), nullable=False)
    account_number = Column(String(100), nullable=False)  # Encrypted
    confirm_account_number = Column(String(100))  # For verification
    ifsc_code = Column(String(50), nullable=False)
    bank_name = Column(String(200))
    branch_name = Column(String(200))
    account_type = Column(String(50))  # savings, current
    
    is_verified = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    verification_document = Column(String(1000))
    verified_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

class Payout(Base):
    __tablename__ = "payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    payout_number = Column(String(100), unique=True, nullable=False)
    payout_type = Column(String(50))  # vendor_payout, refund, settlement
    amount = Column(Float, nullable=False)
    
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="SET NULL"))
    utr_number = Column(String(500))
    
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    bank_account = relationship("BankAccount")
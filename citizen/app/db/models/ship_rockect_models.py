# app/models/order.py
import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("order_addresses.id", ondelete="SET NULL"))
    discount_id = Column(UUID(as_uuid=True), ForeignKey("discounts.id", ondelete="SET NULL"))

    # Order details
    status = Column(String(50), default="pending", index=True)  # pending, confirmed, processing, printing_started, shipped, delivered, canceled, refunded, failed
    fulfillment_status = Column(String(50), default="unfulfilled")  # unfulfilled, partially_fulfilled, fulfilled
    payment_status = Column(String(50), default="pending")  # pending, paid, partially_paid, refunded, failed
    
    # Amounts
    product_amount = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, default=0)
    gift_wrap_amount = Column(Float, default=0)
    shipping_amount = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0)
    
    # Customer notes
    customer_notes = Column(Text)
    admin_notes = Column(Text)
    cancel_reason = Column(Text)
    canceled_at = Column(DateTime)
    
    # Tracking
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime)
    processed_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    expected_delivery_start = Column(DateTime)
    expected_delivery_end = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="orders")
    address = relationship("OrderAddress", back_populates="orders")
    discount = relationship("Discount", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    files = relationship("OrderFile", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", uselist=False, back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")
    email_logs = relationship("OrderEmailLog", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"))
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"))

    # Product snapshot
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(100), nullable=False)
    variant_attributes = Column(JSON)
    
    # Pricing
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)  # Base price per unit
    discount_amount = Column(Float, default=0)  # Discount per unit
    tax_percent = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)  # (price - discount) * quantity + tax
    
    # Shipping dimensions
    weight = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    
    # Status
    is_printed = Column(Boolean, default=False)
    printed_at = Column(DateTime)
    is_shipped = Column(Boolean, default=False)
    shipped_at = Column(DateTime)
    is_delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant")
    files = relationship("OrderFile", back_populates="order_item")

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    status_from = Column(String(50))
    status_to = Column(String(50), nullable=False)
    changed_by = Column(String(100))  # system, user, admin
    changed_by_id = Column(UUID(as_uuid=True))  # user_id if changed by user/admin
    reason = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="status_history")

class OrderFile(Base):
    __tablename__ = "order_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="CASCADE"))
    file_type = Column(String(50))  # design, proof, artwork, invoice, label
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    is_public = Column(Boolean, default=False)
    uploaded_by = Column(String(100))  # user, admin, system
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="files")
    order_item = relationship("OrderItem", back_populates="files")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    invoice_number = Column(String(100), unique=True, nullable=False)
    invoice_url = Column(String(1000))
    invoice_file = Column(String(1000))
    tax_invoice_url = Column(String(1000))  # For GST invoice
    is_gst_invoice = Column(Boolean, default=False)
    invoice_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="invoice")





class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    # Shipment details
    shipment_number = Column(String(100), unique=True, nullable=False)
    carrier = Column(String(100))  # ShipRocket, Delhivery, etc.
    service_provider = Column(String(100))  # Specific service
    shipping_method = Column(String(100))
    
    # Tracking
    tracking_number = Column(String(200), index=True)
    awb_code = Column(String(200), unique=True)
    tracking_url = Column(String(1000))
    
    # Status
    status = Column(String(50), default="pending", index=True)  # pending, confirmed, picked_up, in_transit, out_for_delivery, delivered, failed, returned
    substatus = Column(String(100))
    
    # Dates
    shipped_date = Column(DateTime)
    estimated_delivery_date = Column(DateTime)
    delivered_date = Column(DateTime)
    returned_date = Column(DateTime)
    
    # Package details
    total_weight = Column(Float)
    total_value = Column(Float)
    
    # ShipRocket specific
    shiprocket_order_id = Column(Integer, ForeignKey("shiprocket_orders.id", ondelete="SET NULL"), unique=True)
    shiprocket_shipment_id = Column(Integer, unique=True)
    shiprocket_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="shipments")
    packages = relationship("ShipmentPackage", back_populates="shipment", cascade="all, delete-orphan")
    tracking_events = relationship("ShipmentTracking", back_populates="shipment", cascade="all, delete-orphan")
    labels = relationship("ShipmentLabel", back_populates="shipment", cascade="all, delete-orphan")
    manifests = relationship("ShipmentManifest", back_populates="shipment", cascade="all, delete-orphan")
    ndr_attempts = relationship("NDRAttempt", back_populates="shipment", cascade="all, delete-orphan")
    returns = relationship("ShipmentReturn", back_populates="shipment", cascade="all, delete-orphan")
    cod_settlements = relationship("CODSettlement", back_populates="shipment", cascade="all, delete-orphan")
    
    # ShipRocket specific
    shiprocket_order = relationship("ShipRocketOrder", back_populates="shipments")

class ShipmentPackage(Base):
    __tablename__ = "shipment_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="SET NULL"))
    
    package_number = Column(String(100))
    weight = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="packages")
    order_item = relationship("OrderItem")

class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    
    awb_code = Column(String(200))
    status = Column(String(100))
    location = Column(String(500))
    activity = Column(Text)
    activity_date = Column(DateTime)
    
    raw_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="tracking_events")

class ShipmentLabel(Base):
    __tablename__ = "shipment_labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    
    label_url = Column(String(1000))
    label_file = Column(String(1000))
    label_format = Column(String(20))  # PDF, ZPL, etc.
    
    raw_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="labels")

class ShipmentManifest(Base):
    __tablename__ = "shipment_manifests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    
    manifest_number = Column(String(100))
    manifest_url = Column(String(1000))
    manifest_file = Column(String(1000))
    
    raw_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="manifests")

class NDRAttempt(Base):
    __tablename__ = "ndr_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    
    awb_code = Column(String(200))
    reason = Column(String(500))
    action_taken = Column(String(200))
    status = Column(String(50), default="open")  # open, resolved, ignored
    customer_contacted = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    
    raw_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    shipment = relationship("Shipment", back_populates="ndr_attempts")

class ShipmentReturn(Base):
    __tablename__ = "shipment_returns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    return_number = Column(String(100), unique=True)
    return_reason = Column(String(500))
    return_status = Column(String(50), default="requested")  # requested, approved, picked_up, received, completed, rejected
    return_type = Column(String(50))  # refund, replacement
    return_awb = Column(String(200))
    return_label_url = Column(String(1000))
    return_tracking_url = Column(String(1000))
    
    refund_amount = Column(Float)
    refund_initiated_at = Column(DateTime)
    refund_completed_at = Column(DateTime)
    
    raw_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="returns")
    order = relationship("Order")

class CODSettlement(Base):
    __tablename__ = "cod_settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    awb_code = Column(String(200), index=True)
    order_amount = Column(Float)
    shipping_charges = Column(Float)
    cod_charges = Column(Float)
    other_charges = Column(Float)
    net_receivable = Column(Float)
    settlement_amount = Column(Float)
    
    settlement_status = Column(String(50), default="pending")  # pending, processed, settled, failed
    settlement_date = Column(DateTime)
    settlement_reference = Column(String(200))
    bank_account = Column(String(200))
    
    raw_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="cod_settlements")
    order = relationship("Order")

# ShipRocket specific tables
class ShipRocketAuth(Base):
    __tablename__ = "shiprocket_auth"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ShipRocketOrder(Base):
    __tablename__ = "shiprocket_orders"

    id = Column(Integer, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), unique=True)
    
    shiprocket_order_id = Column(Integer, unique=True, nullable=False)
    shiprocket_shipment_id = Column(Integer, unique=True)
    
    pickup_location_id = Column(Integer, ForeignKey("shiprocket_pickup_locations.id", ondelete="SET NULL"))
    
    order_data = Column(JSON)
    status = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipments = relationship("Shipment", back_populates="shiprocket_order")
    pickup_location = relationship("ShipRocketPickupLocation", back_populates="shiprocket_orders")

class ShipRocketCourier(Base):
    __tablename__ = "shiprocket_couriers"

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, unique=True, nullable=False)
    courier_name = Column(String, nullable=False)
    courier_code = Column(String)
    etd = Column(String)
    is_cod = Column(Boolean, default=True)
    is_prepaid = Column(Boolean, default=True)
    is_reverse = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rates = relationship("ShipRocketCourierRate", back_populates="courier")

class ShipRocketCourierRate(Base):
    __tablename__ = "shiprocket_courier_rates"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"))
    shipment_id = Column(UUID(as_uuid=True), ForeignKey("shipments.id", ondelete="SET NULL"))

    courier_id = Column(Integer, ForeignKey("shiprocket_couriers.id"))
    courier_name = Column(String)
    
    rate = Column(Float)
    estimated_days = Column(Integer)
    is_selected = Column(Boolean, default=False)
    
    pickup_pincode = Column(String)
    delivery_pincode = Column(String)
    weight = Column(Float)
    cod = Column(Boolean, default=False)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    courier = relationship("ShipRocketCourier", back_populates="rates")
    order = relationship("Order")
    shipment = relationship("Shipment")

class ShipRocketPickupLocation(Base):
    __tablename__ = "shiprocket_pickup_locations"

    id = Column(Integer, primary_key=True)
    pickup_location_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    address_2 = Column(Text)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, default="India")
    pincode = Column(String, nullable=False)
    
    lat = Column(String)  # optional 
    long = Column(String)   # optional
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    opening_time = Column(String)
    closing_time = Column(String)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow)

    shiprocket_orders = relationship("ShipRocketOrder", back_populates="pickup_location")





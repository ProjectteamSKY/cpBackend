import uuid
from datetime import datetime
from sqlalchemy import JSON, BigInteger, Column, Float, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

# ==============================================================================
# E-COMMERCE TABLES
# ==============================================================================

class OrderAddress(Base):
    """Customer address for orders"""
    __tablename__ = "order_addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_line = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    phone_number = Column(String(30))
    alt_phone_number = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")


class Order(Base):
    """Main orders table"""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    address_id = Column(UUID(as_uuid=True), ForeignKey("order_addresses.id", ondelete="SET NULL"))
    discount_id = Column(UUID(as_uuid=True), ForeignKey("discounts.id", ondelete="SET NULL"))

    # Order status
    status = Column(String(50), default="pending")  # pending, printing_started, shipped, delivered, canceled, refunded
    cancel_reason = Column(Text, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    
    # Financial details
    product_amount = Column(Float)
    gst_amount = Column(Float)
    shipping_amount = Column(Float)
    total_amount = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    product = relationship("Product", foreign_keys=[product_id], back_populates="orders")
    address = relationship("OrderAddress", back_populates="orders")
    discount = relationship("Discount", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipment = relationship("Shipment", uselist=False, back_populates="order", cascade="all, delete-orphan")
    files = relationship("OrderFile", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", uselist=False, back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")
    
    # ShipRocket relationships
    shiprocket_order = relationship("ShipRocketOrder", back_populates="order", uselist=False)
    shiprocket_rates = relationship("ShipRocketCourierRate", back_populates="order")
    shiprocket_returns = relationship("ShipRocketReturn", back_populates="order")
    shiprocket_cod_settlements = relationship("ShipRocketCODSettlement", back_populates="order")

    @property
    def expected_delivery_date(self):
        """Convenience property to get shipment's expected delivery for user display."""
        return self.shipment.expected_delivery if self.shipment else None
    
    @property
    def main_product(self):
        """Get the main product for the order (first item or direct product_id)"""
        if self.product_id:
            return self.product
        elif self.items and len(self.items) > 0:
            return self.items[0].product
        return None


class OrderItem(Base):
    """Individual items within an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=False)

    # Quantity and pricing
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    gst_percent = Column(Float, default=0)
    gst_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)

    # Physical attributes
    weight = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", foreign_keys=[product_id], back_populates="order_items")


class Refund(Base):
    """Order refunds"""
    __tablename__ = "refunds"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(BigInteger, ForeignKey("payments.id", ondelete="SET NULL"))

    refund_amount = Column(Float, nullable=False)
    refund_status = Column(String, default="pending")
    refund_transaction_id = Column(String, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="refunds")
    payment = relationship("Payment", back_populates="refunds")


# ==============================================================================
# SHIPROCKET INTEGRATION TABLES
# ==============================================================================

class ShipRocketAuth(Base):
    """ShipRocket authentication tokens"""
    __tablename__ = "shiprocket_auth"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShipRocketPickupLocation(Base):
    """Pickup locations configured in ShipRocket"""
    __tablename__ = "shiprocket_pickup_locations"

    id = Column(Integer, primary_key=True)
    pickup_location_id = Column(Integer,  primary_key=True, index=True)
    
    # Location details
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    pincode = Column(String)
    
    is_active = Column(Boolean, default=True)
    pickup_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shiprocket_orders = relationship("ShipRocketOrder", back_populates="pickup_location")


class ShipRocketCourier(Base):
    """Available couriers from ShipRocket"""
    __tablename__ = "shiprocket_couriers"

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, unique=True, nullable=False)
    courier_name = Column(String, nullable=False)
    courier_code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    rates = relationship("ShipRocketCourierRate", back_populates="courier")
    shipments = relationship("ShipRocketShipment", back_populates="courier")


class ShipRocketCourierRate(Base):
    """Shipping rates for orders from different couriers"""
    __tablename__ = "shiprocket_courier_rates"

    id = Column(BigInteger, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    courier_id = Column(Integer, ForeignKey("shiprocket_couriers.id"), nullable=False)

    rate = Column(Float, nullable=False)
    estimated_days = Column(Integer)
    is_selected = Column(Boolean, default=False)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    courier = relationship("ShipRocketCourier", back_populates="rates")
    order = relationship("Order", back_populates="shiprocket_rates")


class ShipRocketServiceability(Base):
    """Serviceability checks for delivery locations"""
    __tablename__ = "shiprocket_serviceability"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)

    pickup_postcode = Column(String, nullable=False)
    delivery_postcode = Column(String, nullable=False)

    courier_id = Column(Integer, nullable=False)
    courier_name = Column(String)
    estimated_days = Column(Integer)
    rate = Column(Float)

    serviceability_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShipRocketOrder(Base):
    """ShipRocket order mapping"""
    __tablename__ = "shiprocket_orders"

    id = Column(Integer, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    pickup_location_id = Column(Integer, ForeignKey("shiprocket_pickup_locations.id"), nullable=False)

    shiprocket_order_id = Column(Integer, unique=True, nullable=False)
    order_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="shiprocket_order")
    pickup_location = relationship("ShipRocketPickupLocation", back_populates="shiprocket_orders")
    shipment = relationship("ShipRocketShipment", back_populates="shiprocket_order", uselist=False)


class ShipRocketShipment(Base):
    """Shipments created in ShipRocket"""
    __tablename__ = "shiprocket_shipments"

    id = Column(Integer, primary_key=True)
    shiprocket_order_id = Column(Integer, ForeignKey("shiprocket_orders.id", ondelete="CASCADE"), nullable=False)
    courier_id = Column(Integer, ForeignKey("shiprocket_couriers.id"), nullable=False)

    awb_code = Column(String, unique=True, nullable=False)
    shipment_status = Column(String, default="pending")
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)

    shipment_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shiprocket_order = relationship("ShipRocketOrder", back_populates="shipment")
    courier = relationship("ShipRocketCourier", back_populates="shipments")
    labels = relationship("ShipRocketLabel", back_populates="shipment", cascade="all, delete-orphan")
    manifests = relationship("ShipRocketManifest", back_populates="shipment", cascade="all, delete-orphan")
    tracking = relationship("ShipRocketTracking", back_populates="shipment", cascade="all, delete-orphan")
    ndr = relationship("ShipRocketNDR", back_populates="shipment", cascade="all, delete-orphan")
    returns = relationship("ShipRocketReturn", back_populates="shipment")
    cod_settlements = relationship("ShipRocketCODSettlement", back_populates="shipment")


class ShipRocketInvoice(Base):
    """ShipRocket invoices"""
    __tablename__ = "shiprocket_invoices"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, index=True, nullable=False)

    invoice_url = Column(String, nullable=False)
    invoice_file = Column(String, nullable=True)
    invoice_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShipRocketLabel(Base):
    """Shipping labels from ShipRocket"""
    __tablename__ = "shiprocket_labels"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"), nullable=False)

    label_url = Column(String, nullable=False)
    label_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("ShipRocketShipment", back_populates="labels")


class ShipRocketManifest(Base):
    """Manifest documents from ShipRocket"""
    __tablename__ = "shiprocket_manifests"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"), nullable=False)

    manifest_url = Column(String, nullable=False)
    manifest_file = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("ShipRocketShipment", back_populates="manifests")


class ShipRocketTracking(Base):
    """Shipment tracking information"""
    __tablename__ = "shiprocket_tracking"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"), nullable=False)

    awb_code = Column(String, nullable=False)
    status = Column(String)
    location = Column(String)
    activity = Column(Text)
    activity_date = Column(DateTime)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("ShipRocketShipment", back_populates="tracking")


class ShipRocketNDR(Base):
    """Non-Delivery Reports (NDR) handling"""
    __tablename__ = "shiprocket_ndr"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"), nullable=False)

    awb_code = Column(String, nullable=False)
    ndr_reason = Column(String)
    action_taken = Column(String)
    ndr_status = Column(String, default="open")
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("ShipRocketShipment", back_populates="ndr")


class ShipRocketReturn(Base):
    """Return shipments"""
    __tablename__ = "shiprocket_returns"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    return_id = Column(Integer, unique=True, nullable=False)
    awb_code = Column(String)
    reason = Column(String)
    status = Column(String, default="requested")
    label_url = Column(String)
    return_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("ShipRocketShipment", back_populates="returns")
    order = relationship("Order", back_populates="shiprocket_returns")


class ShipRocketCODSettlement(Base):
    """COD (Cash on Delivery) settlements"""
    __tablename__ = "shiprocket_cod_settlements"

    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    awb_code = Column(String, index=True, nullable=False)
    order_amount = Column(Float, nullable=False)
    shipping_charges = Column(Float)
    cod_charges = Column(Float)
    remittance_amount = Column(Float)
    remittance_status = Column(String, default="pending")
    remittance_date = Column(DateTime)
    settlement_payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("ShipRocketShipment", back_populates="cod_settlements")
    order = relationship("Order", back_populates="shiprocket_cod_settlements")
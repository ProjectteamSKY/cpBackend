import uuid
from datetime import datetime
from sqlalchemy import JSON, BigInteger, Column, Float, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrderAddress(Base):
    __tablename__ = "order_addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_line = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    phone_number = Column(String(30))
    alt_phone_number = Column(String(30))       # alternative
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")  


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("order_addresses.id", ondelete="SET NULL"))
    discount_id = Column(UUID(as_uuid=True), ForeignKey("discounts.id", ondelete="SET NULL"))

    # Status & cancellation
    status = Column(String(50), default="pending")  # pending, printing_started, shipped, delivered, canceled, refunded
    cancel_reason = Column(Text, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    product_amount = Column(Float)
    gst_amount = Column(Float)

    shipping_amount = Column(Float)

    total_amount = Column(Float)
    # Payment info

    # Record timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    address = relationship("UserAddress", back_populates="orders")
    discount = relationship("Discount", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipment = relationship("Shipment", uselist=False, back_populates="order", cascade="all, delete-orphan")
    files = relationship("OrderFile", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", uselist=False, back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    @property
    def expected_delivery(self):
        """Convenience property to get shipment's expected delivery for user display."""
        return self.shipment.expected_delivery if self.shipment else None


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(UUID(as_uuid=True),ForeignKey("orders.id"))

    product_id = Column(UUID(as_uuid=True),ForeignKey("products.id"))

    quantity = Column(Integer)

    price = Column(Float)

    gst_percent = Column(Float)

    gst_amount = Column(Float)

    total_amount = Column(Float)

    weight = Column(Float)

    length = Column(Float)
    width = Column(Float)
    height = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())





from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ShipRocketAuth(Base):
    __tablename__ = "shiprocket_auth"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String)
    token = Column(Text)

    expires_at = Column(DateTime)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ShipRocketCourier(Base):
    __tablename__ = "shiprocket_couriers"

    id = Column(Integer, primary_key=True)

    courier_id = Column(Integer, unique=True)
    courier_name = Column(String)
    courier_code = Column(String)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    rates = relationship("ShipRocketCourierRate",
                         back_populates="courier")

class ShipRocketServiceability(Base):
    __tablename__ = "shiprocket_serviceability"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, index=True)

    pickup_postcode = Column(String)
    delivery_postcode = Column(String)

    courier_id = Column(Integer)
    courier_name = Column(String)

    estimated_days = Column(Integer)

    rate = Column(Float)

    serviceability_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShipRocketCourierRate(Base):
    __tablename__ = "shiprocket_courier_rates"

    id = Column(BigInteger, primary_key=True)

    order_id = Column(UUID(as_uuid=True),
                      ForeignKey("orders.id", ondelete="CASCADE"))

    courier_id = Column(Integer,
                        ForeignKey("shiprocket_couriers.id"))

    rate = Column(Float)
    estimated_days = Column(Integer)

    is_selected = Column(Boolean, default=False)

    payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    courier = relationship("ShipRocketCourier",
                           back_populates="rates")

    order = relationship("Order")



class ShipRocketShipment(Base):
    __tablename__ = "shiprocket_shipments"

    id = Column(Integer, primary_key=True)

    shiprocket_order_id = Column(Integer,
                                 ForeignKey("shiprocket_orders.id",
                                            ondelete="CASCADE"))

    awb_code = Column(String, unique=True)

    courier_id = Column(Integer,
                        ForeignKey("shiprocket_couriers.id"))

    shipment_status = Column(String)

    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)

    shipment_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    shiprocket_order = relationship("ShipRocketOrder",
                                    back_populates="shipment")

    courier = relationship("ShipRocketCourier")


class ShipRocketInvoice(Base):
    __tablename__ = "shiprocket_invoices"

    id = Column(Integer, primary_key=True, index=True)

    shipment_id = Column(Integer, index=True)

    invoice_url = Column(String)

    invoice_file = Column(String, nullable=True)

    invoice_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())



class ShipRocketLabel(Base):
    __tablename__ = "shiprocket_labels"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id",
                                    ondelete="CASCADE"))

    label_url = Column(String)

    label_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())


class ShipRocketManifest(Base):
    __tablename__ = "shiprocket_manifests"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
        ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"))

    manifest_url = Column(String)

    manifest_file = Column(String)

    payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    shipment = relationship("ShipRocketShipment")



class ShipRocketTracking(Base):
    __tablename__ = "shiprocket_tracking"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id",
                                    ondelete="CASCADE"))

    awb_code = Column(String)

    status = Column(String)

    location = Column(String)

    activity = Column(Text)

    activity_date = Column(DateTime)

    payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

class ShipRocketNDR(Base):
    __tablename__ = "shiprocket_ndr"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
        ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"))

    awb_code = Column(String)

    ndr_reason = Column(String)

    action_taken = Column(String)

    ndr_status = Column(String, default="open")

    payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    shipment = relationship("ShipRocketShipment")



class ShipRocketReturn(Base):
    __tablename__ = "shiprocket_returns"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
        ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"))

    order_id = Column(UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"))

    return_id = Column(Integer, unique=True)

    awb_code = Column(String)

    reason = Column(String)

    status = Column(String, default="requested")

    label_url = Column(String)

    return_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    shipment = relationship("ShipRocketShipment")

    order = relationship("Order")



class ShipRocketCODSettlement(Base):
    __tablename__ = "shiprocket_cod_settlements"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
        ForeignKey("shiprocket_shipments.id", ondelete="CASCADE"))

    order_id = Column(UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"))

    awb_code = Column(String, index=True)

    order_amount = Column(Float)

    shipping_charges = Column(Float)

    cod_charges = Column(Float)

    remittance_amount = Column(Float)

    remittance_status = Column(String, default="pending")

    remittance_date = Column(DateTime)

    settlement_payload = Column(JSON)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    shipment = relationship("ShipRocketShipment")

    order = relationship("Order")



class ShipRocketPickupLocation(Base):
    __tablename__ = "shiprocket_pickup_locations"

    id = Column(Integer, primary_key=True)

    pickup_location_id = Column(Integer, unique=True, index=True)

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

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    shiprocket_orders = relationship(
        "ShipRocketOrder",
        back_populates="pickup_location"
    )





class Refund(Base):
    __tablename__ = "refunds"

    id = Column(BigInteger, primary_key=True)

    order_id = Column(BigInteger)

    payment_id = Column(BigInteger)

    refund_amount = Column(Float)

    refund_status = Column(String)

    refund_transaction_id = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

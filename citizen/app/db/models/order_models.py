import uuid
from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# =========================================================
# ORDER ADDRESS
# =========================================================

class OrderAddress(Base):
    __tablename__ = "order_addresses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String(36),
                     ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False)

    address = Column(Text, nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    phone = Column(String(20))

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    orders = relationship("Order", back_populates="address")


# =========================================================
# ORDER
# =========================================================

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String(36),
                     ForeignKey("users.id", ondelete="CASCADE"))

    address_id = Column(String(36),
                        ForeignKey("order_addresses.id"))

    status = Column(String(50), default="pending")
    # pending, paid, shipped, delivered, cancelled

    total_amount = Column(Float, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    address = relationship("OrderAddress", back_populates="orders")

    items = relationship("OrderItem",
                         back_populates="order",
                         cascade="all, delete-orphan")

    shiprocket_order = relationship("ShipRocketOrder",
                                    back_populates="order",
                                    uselist=False)


# =========================================================
# ORDER ITEMS
# =========================================================

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    order_id = Column(String(36),
                      ForeignKey("orders.id", ondelete="CASCADE"))

    product_id = Column(String(36),
                        ForeignKey("products.id"))

    quantity = Column(Integer, nullable=False)

    price = Column(Float, nullable=False)

    total = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")


class ShipRocketAuth(Base):
    __tablename__ = "shiprocket_auth"

    id = Column(Integer, primary_key=True)

    token = Column(Text, nullable=False)

    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, server_default=func.now())


class ShipRocketPickupLocation(Base):
    __tablename__ = "shiprocket_pickup_locations"

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    address = Column(Text)

    city = Column(String(100))

    state = Column(String(100))

    country = Column(String(100))

    pincode = Column(String(20))

    phone = Column(String(20))

    created_at = Column(DateTime, server_default=func.now())

    shiprocket_orders = relationship("ShipRocketOrder", back_populates="pickup_location")

    

class ShipRocketOrder(Base):
    __tablename__ = "shiprocket_orders"

    id = Column(Integer, primary_key=True)

    order_id = Column(String(36),
                      ForeignKey("orders.id", ondelete="CASCADE"))

    pickup_location_id = Column(Integer,
                                ForeignKey("shiprocket_pickup_locations.id"))

    shiprocket_order_id = Column(Integer, unique=True)

    created_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="shiprocket_order")

    pickup_location = relationship("ShipRocketPickupLocation",
                                   back_populates="shiprocket_orders")

    shipment = relationship("ShipRocketShipment",
                            back_populates="shiprocket_order",
                            uselist=False)

class ShipRocketCourier(Base):
    __tablename__ = "shiprocket_couriers"

    id = Column(Integer, primary_key=True)

    courier_id = Column(Integer, unique=True)

    name = Column(String(100))

    created_at = Column(DateTime, server_default=func.now())


class ShipRocketCourierRate(Base):
    __tablename__ = "shiprocket_courier_rates"

    id = Column(Integer, primary_key=True)

    courier_id = Column(Integer,
                        ForeignKey("shiprocket_couriers.id"))

    rate = Column(Float)

    estimated_days = Column(Integer)

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketServiceability(Base):
    __tablename__ = "shiprocket_serviceability"

    id = Column(Integer, primary_key=True)

    courier_id = Column(Integer,
                        ForeignKey("shiprocket_couriers.id"))

    pickup_pincode = Column(String(20))

    delivery_pincode = Column(String(20))

    is_serviceable = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())





class ShipRocketShipment(Base):
    __tablename__ = "shiprocket_shipments"

    id = Column(Integer, primary_key=True)

    shiprocket_order_id = Column(Integer,
                                 ForeignKey("shiprocket_orders.id"))

    courier_id = Column(Integer,
                        ForeignKey("shiprocket_couriers.id"))

    awb_code = Column(String(100), unique=True)

    status = Column(String(50))

    shipped_at = Column(DateTime)

    delivered_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

    shiprocket_order = relationship("ShipRocketOrder",
                                    back_populates="shipment")

    courier = relationship("ShipRocketCourier")

class ShipRocketInvoice(Base):
    __tablename__ = "shiprocket_invoices"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    invoice_number = Column(String(100))

    invoice_url = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketLabel(Base):
    __tablename__ = "shiprocket_labels"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    label_url = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketManifest(Base):
    __tablename__ = "shiprocket_manifests"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    manifest_url = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketTracking(Base):
    __tablename__ = "shiprocket_tracking"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    status = Column(String(100))

    location = Column(String(255))

    message = Column(Text)

    tracked_at = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketNDR(Base):
    __tablename__ = "shiprocket_ndr"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    reason = Column(Text)

    status = Column(String(50))

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketReturn(Base):
    __tablename__ = "shiprocket_returns"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    status = Column(String(50))

    created_at = Column(DateTime, server_default=func.now())

class ShipRocketCODSettlement(Base):
    __tablename__ = "shiprocket_cod_settlements"

    id = Column(Integer, primary_key=True)

    shipment_id = Column(Integer,
                         ForeignKey("shiprocket_shipments.id"))

    amount = Column(Float)

    settlement_date = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())

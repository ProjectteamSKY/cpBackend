
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


# -------------------------
#  Category
# -------------------------
class Category(Base):
    """Stores main product categories like Business Cards, Invitations, Flyers, etc."""
    __tablename__ = "categories"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    subcategories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


# -------------------------
#  SubCategory
# -------------------------
class SubCategory(Base):
    """Stores subcategories under each category, e.g., Corporate, Personal, Wedding."""
    __tablename__ = "subcategories"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory", cascade="all, delete-orphan")


# -------------------------
#  ProductType
# -------------------------
class ProductType(Base):
    """Defines types of products, e.g., Standard, Premium, Digital."""
    __tablename__ = "product_types"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="product_type_rel", cascade="all, delete-orphan")


# -------------------------
#  PaperType
# -------------------------
class PaperType(Base):
    """Stores available paper types for print products, e.g., Matte, Glossy, Cardstock."""
    __tablename__ = "paper_types"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product_variants = relationship("ProductVariant", back_populates="paper_type", cascade="all, delete-orphan")


# -------------------------
#  Finish
# -------------------------
class Finish(Base):
    """Stores finishing options for printed products, e.g., Lamination, UV Coating, Embossing."""
    __tablename__ = "finishes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product_variants = relationship("ProductVariant", back_populates="finish", cascade="all, delete-orphan")


# -------------------------
#  Product
# -------------------------
class Product(Base):
    """Main product catalog storing basic info like name, description, dimensions, base price, GST."""
    __tablename__ = "products"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"))
    subcategory_id = Column(String(36), ForeignKey("subcategories.id", ondelete="SET NULL"))
    product_type_id = Column(String(36), ForeignKey("product_types.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    base_price = Column(Float, nullable=False)
    gst_percent = Column(Float, default=0)
    weight = Column(Float, default=0)
    length = Column(Float, default=0)
    width = Column(Float, default=0)
    height = Column(Float, default=0)
    min_order_qty = Column(Integer, default=1)
    max_order_qty = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    product_type_rel = relationship("ProductType", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class CutType(Base):
    """Stores available cut types for products, e.g., Die Cut, Straight Cut, Rounded Corner."""
    __tablename__ = "cut_types"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product_variants = relationship("ProductVariant", back_populates="cut_type", cascade="all, delete-orphan")

# -------------------------
#  ProductVariant
# -------------------------
class ProductVariant(Base):
    """Specific variant of a product including size, paper type, finish, price, cut type, and optional attributes."""
    __tablename__ = "product_variants"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"))
    paper_type_id = Column(String(36), ForeignKey("paper_types.id", ondelete="SET NULL"))
    finish_id = Column(String(36), ForeignKey("finishes.id", ondelete="SET NULL"))
    cut_type_id = Column(String(36), ForeignKey("cut_types.id", ondelete="SET NULL"))
    size = Column(String(50))          # e.g., A4, A3, #10 Envelope
    sides = Column(Integer, default=1) # 1=Single sided, 2=Double sided
    orientation = Column(String(20), default="Portrait")
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="variants")
    paper_type = relationship("PaperType", back_populates="product_variants")
    finish = relationship("Finish", back_populates="product_variants")
    cut_type = relationship("CutType", back_populates="product_variants")



# -------------------------
#  ProductImage
# -------------------------
class ProductImage(Base):
    """Stores images for each product; includes default image flag."""
    __tablename__ = "product_images"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(String(500), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="images")


# -------------------------
#  SheetTemplate
# -------------------------
class SheetTemplate(Base):
    """Defines sheet size and layout info to calculate how many cards fit per sheet."""
    __tablename__ = "sheet_templates"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sheet_type = Column(String(50))       # A4, A3, Letter
    card_width = Column(Float)            # width of a single card
    card_height = Column(Float)           # height of a single card
    max_cards_per_sheet = Column(Integer) # precomputed or optional
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

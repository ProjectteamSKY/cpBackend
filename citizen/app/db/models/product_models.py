
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, UniqueConstraint
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory", cascade="all, delete-orphan")


# -------------------------
#  ProductType
# -------------------------


class ProductType(Base):
    __tablename__ = "product_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)   # ✅ ADD THIS
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    products = relationship(
        "Product",
        back_populates="product_type",
        cascade="all, delete-orphan"
    )



# -------------------------
#  PaperType
# -------------------------


class PaperType(Base):
    """Stores available paper types for print products, e.g., Matte, Glossy, Cardstock."""
    __tablename__ = "paper_types"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product_variants = relationship("ProductVariant", back_populates="paper_type", cascade="all, delete-orphan")


# -------------------------
#  Finish
# -------------------------


class Printing_type(Base):
    """Stores finishing options for printed products, e.g., Lamination, UV Coating, Embossing."""
    __tablename__ = "finishes"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product_variants = relationship("ProductVariant", back_populates="finish", cascade="all, delete-orphan")



class CutType(Base):
    """Stores available cut types for products, e.g., Die Cut, Straight Cut, Rounded Corner."""
    __tablename__ = "cut_types"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    product_variants = relationship("ProductVariant", back_populates="cut_type", cascade="all, delete-orphan")


# =========================================================
# CUSTOM SHAPE
# =========================================================

class CustomShape(Base):
    __tablename__ = "custom_shapes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean,default=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    variants = relationship("ProductVariant", back_populates="shape")


# -------------------------
#  Size (Reference Table)
# -------------------------

class Size(Base):
    """Normalized size reference table - stores each unique size once"""
    __tablename__ = "sizes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # Display name: "A4", "Business Card", "8x2"
    width = Column(Float, nullable=False)       # in mm
    height = Column(Float, nullable=False)      # in mm
    unit = Column(String(10), default="mm")
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    variants = relationship("ProductVariant", back_populates="size")
    
    __table_args__ = (
        UniqueConstraint("width", "height", name="uq_size_dimensions"),
    )

# -------------------------
#  Product
# -------------------------

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"))
    subcategory_id = Column(String(36), ForeignKey("subcategories.id", ondelete="SET NULL"))
    product_type_id = Column(String(36), ForeignKey("product_types.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    min_order_qty = Column(Integer, default=100)
    max_order_qty = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    product_type = relationship("ProductType", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")




# =========================================================
# PRODUCT VARIANT
# =========================================================

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"))
    size_id = Column(String(36), ForeignKey("sizes.id"), nullable=False)
    paper_type_id = Column(String(36), ForeignKey("paper_types.id"))
    finish_id = Column(String(36), ForeignKey("finishes.id"))
    cut_type_id = Column(String(36), ForeignKey("cut_types.id"))
    shape_id = Column(String(36), ForeignKey("custom_shapes.id"))
    sides = Column(Integer)    # 1 or 2
    two_side_cut = Column(Boolean, default=False)
    four_side_cut = Column(Boolean, default=False)
    orientation = Column(String(20), default="Portrait")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product = relationship("Product", back_populates="variants")
    paper_type = relationship("PaperType", back_populates="product_variants")
    finish = relationship("Finish", back_populates="product_variants")
    cut_type = relationship("CutType", back_populates="product_variants")
    shape = relationship("CustomShape", back_populates="variants")
    size = relationship("Size", back_populates="variants")
    prices = relationship("ProductVariantPrice", back_populates="variant", cascade="all, delete-orphan")

    



# =========================================================
# VARIANT PRICE (MOST IMPORTANT TABLE)
# =========================================================


class ProductVariantPrice(Base):
    __tablename__ = "product_variant_prices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    variant_id = Column(String(36), ForeignKey("product_variants.id", ondelete="CASCADE"))
    min_qty = Column(Integer, nullable=False)
    max_qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean,default=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    variant = relationship("ProductVariant", back_populates="prices")
    __table_args__ = (
        UniqueConstraint("variant_id", "min_qty", "max_qty"),
    )

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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    product = relationship("Product", back_populates="images")



class ProductRelatedImage(Base):
    __tablename__ = "product_related_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"))
    image_url = Column(String(500), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # product = relationship("Product", back_populates="images")

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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


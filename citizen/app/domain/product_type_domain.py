import uuid
from datetime import datetime
from typing import Optional, List

from app.domain.product_domain import Product


class ProductType:
    """
    Represents a type or classification of products in the domain.
    Example types: Standard, Premium, Digital.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id: uuid.UUID = id or uuid.uuid4()
        self.name: str = name
        self.description: Optional[str] = description
        self.is_active: bool = is_active
        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

        # Related products (aggregate)
        self.products: List["Product"] = []

    # ---------------------------
    # Behavior / Domain Methods
    # ---------------------------
    def activate(self):
        """Activate this product type."""
        self.is_active = True
        self.touch()

    def deactivate(self):
        """Deactivate this product type."""
        self.is_active = False
        self.touch()

    def rename(self, new_name: str):
        """Rename the product type."""
        if not new_name:
            raise ValueError("Product type name cannot be empty")
        self.name = new_name
        self.touch()

    def update_description(self, new_description: Optional[str]):
        """Update description."""
        self.description = new_description
        self.touch()

    def add_product(self, product: "Product"):
        """Add a product under this type."""
        self.products.append(product)
        self.touch()

    def remove_product(self, product: "Product"):
        """Remove a product from this type."""
        self.products = [p for p in self.products if p.id != product.id]
        self.touch()

    def touch(self):
        """Update the last updated timestamp."""
        self.updated_at = datetime.utcnow()

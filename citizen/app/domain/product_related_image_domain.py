# app/domain/product_related_image_domain.py
import uuid
from datetime import datetime

class ProductRelatedImageDomain:
    """Domain object for a product's related image."""
    def __init__(
        self,
        product_id: str,
        image_url: str,
        is_default: bool = False,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        self.id = id or str(uuid.uuid4())
        self.product_id = product_id
        self.image_url = image_url
        self.is_default = is_default
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self):
        return f"<ProductRelatedImage id={self.id} product_id={self.product_id}>"
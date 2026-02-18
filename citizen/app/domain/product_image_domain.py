import uuid
from datetime import datetime

class ProductImage:
    """Stores images for each product; includes default image flag."""

    def __init__(
        self,
        product_id: str,
        image_url: str,
        is_default: bool = False,
        id: str | None = None,
        created_at: datetime | None = None
    ):
        self.id = id or str(uuid.UUID)
        self.product_id = product_id
        self.image_url = image_url
        self.is_default = is_default
        self.created_at = created_at or datetime.utcnow()

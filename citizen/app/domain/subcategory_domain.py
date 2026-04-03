import uuid
from datetime import datetime
from typing import Optional, List


class Subcategory:

    def __init__(
        self,
        category_id: str,
        name: str,
        description: Optional[str] = None,
        images: Optional[List[dict]] = None,   # ✅ NEW
        is_active: bool = True,
        is_deleted: bool = False,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):

        self.id: str = id or str(uuid.uuid4())
        self.category_id: str = category_id
        self.name: str = name
        self.description: Optional[str] = description

        self.images: List[dict] = images or []   # ✅ NEW FIELD

        self.is_active: bool = is_active
        self.is_deleted: bool = is_deleted

        self.created_at: datetime = created_at or datetime.utcnow()
        self.updated_at: datetime = updated_at or datetime.utcnow()

    # ------------------------
    # Active / Inactive
    # ------------------------

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    # ------------------------
    # Soft Delete Methods
    # ------------------------

    def soft_delete(self):
        self.is_deleted = True
        self.touch()

    def restore(self):
        self.is_deleted = False
        self.touch()

    # ------------------------
    # Image Helpers (🔥 NEW)
    # ------------------------

    def add_image(self, url: str, is_default: bool = False):
        """Add new image"""
        image = {
            "id": str(uuid.uuid4()),
            "url": url,
            "is_default": is_default
        }

        # if default → remove old default
        if is_default:
            for img in self.images:
                img["is_default"] = False

        self.images.append(image)
        self.touch()

    def remove_image(self, image_id: str):
        """Remove image by ID"""
        self.images = [img for img in self.images if img["id"] != image_id]
        self.touch()

    def set_default_image(self, image_id: str):
        """Set one image as default"""
        for img in self.images:
            img["is_default"] = (img["id"] == image_id)
        self.touch()

    # ------------------------
    # Update Methods
    # ------------------------

    def rename(self, new_name: str):
        if not new_name:
            raise ValueError("Subcategory name cannot be empty")

        self.name = new_name
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    # ------------------------
    # Convert to Dict
    # ------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "images": self.images,   # ✅ INCLUDED
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
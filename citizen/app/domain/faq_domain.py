import uuid
from datetime import datetime
from typing import Optional


class FAQ:

    def __init__(
        self,
        question: str,
        answer: str,
        type: str,
        category_id: Optional[str] = None,
        product_id: Optional[str] = None,
        is_active: bool = True,
        sort_order: int = 0,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):

        self.id = id or str(uuid.uuid4())
        self.question = question
        self.answer = answer
        self.type = type

        self.category_id = category_id
        self.product_id = product_id

        self.is_active = is_active
        self.sort_order = sort_order

        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

        self.validate()

    def validate(self):
        if self.type not in ["category", "product"]:
            raise ValueError("Invalid FAQ type")

        if self.type == "category" and not self.category_id:
            raise ValueError("category_id required")

        if self.type == "product" and not self.product_id:
            raise ValueError("product_id required")

    def activate(self):
        self.is_active = True
        self.touch()

    def deactivate(self):
        self.is_active = False
        self.touch()

    def touch(self):
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return self.__dict__
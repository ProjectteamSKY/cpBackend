from typing import Optional

class Role:
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
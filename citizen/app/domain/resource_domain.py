from typing import Optional

class Resource:
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
class Permission:
    def __init__(
        self,
        resource_id: int,
        action: str,
        method: str | None = None,
        path: str | None = None,
        description: str | None = None,
    ):
        self.resource_id = resource_id
        self.action = action
        self.method = method
        self.path = path
        self.description = description
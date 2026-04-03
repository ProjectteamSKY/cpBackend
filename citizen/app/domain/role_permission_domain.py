from datetime import datetime


class RolePermission:
    def __init__(self, role_id: int, permission_id: int):
        self.role_id = role_id
        self.permission_id = permission_id
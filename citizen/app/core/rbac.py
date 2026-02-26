from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class RBACPolicy:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_permission(self, request_path: str, method: str) -> str | None:
       

        result = await self.session.execute(
            text("""
                SELECT res.name || ':' || p.action AS permissions, p.path
                FROM permissions p
                JOIN resources res ON res.id = p.resource_id
                WHERE p.method = :method
            """),
            {"method": method}
        )

        rows = result.fetchall()

        for permission, policy_path in rows:
            if self._match(policy_path, request_path):
                return permission

        return None

    def _match(self, policy_path: str, request_path: str) -> bool:
       
        p = policy_path.strip("/").split("/")
        r = request_path.strip("/").split("/")

        if len(p) != len(r):
            return False

        for a, b in zip(p, r):
            if a.startswith("{") and a.endswith("}"):
                continue
            if a != b:
                return False

        return True

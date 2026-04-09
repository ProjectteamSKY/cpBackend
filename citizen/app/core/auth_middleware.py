# app/core/auth_middleware.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization")

        # default
        request.state.roles = []
        request.state.user_id = None

        if not auth:
            return await call_next(request)

        token = auth.replace("Bearer ", "").strip()

        async with AsyncSessionLocal() as session:

            # ✅ Get user
            result = await session.execute(
                text("""
                    SELECT id
                    FROM users
                    WHERE bearer_token = :token
                    AND is_active = TRUE
                """),
                {"token": token}
            )
            user_row = result.fetchone()

            if not user_row:
                return await call_next(request)

            user_id = user_row[0]
            request.state.user_id = user_id

            # ✅ Get roles
            result_roles = await session.execute(
                text("""
                    SELECT LOWER(r.name)
                    FROM user_roles ur
                    JOIN roles r ON r.id = ur.role_id
                    WHERE ur.user_id = :user_id
                    AND r.is_active = TRUE
                    AND r.is_deleted = FALSE
                """),
                {"user_id": user_id}
            )

            roles = [r[0] for r in result_roles.fetchall()]
            request.state.roles = roles

            print(f"[AuthMiddleware] user_id={user_id}, roles={roles}")

        return await call_next(request)
# app/core/auth_middleware.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text
from app.core.database import SessionLocal


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        auth = request.headers.get("Authorization")
        request.state.roles = []

        if not auth:
            return await call_next(request)

        token = auth.replace("Bearer ", "").strip()

        async with SessionLocal() as session:

            # Get user by token
            result = await session.execute(
                text("SELECT id FROM users WHERE bearer_token = :token"),
                {"token": token}
            )

            user_row = result.fetchone()

            if not user_row:
                return await call_next(request)

            user_id = user_row[0]

            # Fetch roles
            result_roles = await session.execute(
                text("""
                    SELECT LOWER(r.name)
                    FROM user_roles ur
                    JOIN roles r ON r.id = ur.role_id
                    WHERE ur.user_id = :user_id
                """),
                {"user_id": user_id}
            )

            roles = [r[0] for r in result_roles.fetchall()]
            request.state.roles = roles

        print(f"[AuthMiddleware] Roles: {roles}")

        return await call_next(request)
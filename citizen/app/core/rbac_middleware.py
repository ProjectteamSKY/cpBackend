# app/core/rbac_middleware.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text, bindparam
from app.core.database import AsyncSessionLocal
from app.core.rbac import RBACPolicy


class RBACMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        roles = getattr(request.state, "roles", [])

        async with AsyncSessionLocal() as session:

            policy = RBACPolicy(session)

            permission = await policy.get_permission(
                request.url.path,
                request.method
            )

            print(
                f"[RBAC] Path={request.url.path} "
                f"Method={request.method} "
                f"Permission={permission} "
                f"Roles={roles}"
            )

            # ✅ Public route (no permission configured)
            if not permission:
                return await call_next(request)

            # ❌ No roles → deny
            if not roles:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied (no roles)"}
                )

            # ✅ Fetch permissions of roles
            stmt = text("""
                SELECT 
                    CONCAT(res.name, ':', p.action) AS permission
                FROM roles r
                JOIN role_permissions rp ON rp.role_id = r.id
                JOIN permissions p ON p.id = rp.permission_id
                JOIN resources res ON res.id = p.resource_id
                WHERE LOWER(r.name) IN :roles
                AND r.is_active = TRUE
                AND r.is_deleted = FALSE
                AND p.is_active = TRUE
                AND p.is_deleted = FALSE
                AND res.is_active = TRUE
                AND res.is_deleted = FALSE
            """).bindparams(bindparam("roles", expanding=True))

            result = await session.execute(stmt, {"roles": roles})
            permissions = {row[0] for row in result.fetchall()}

            print(f"[RBAC] DB permissions = {permissions}")

            # ✅ Allow
            if permission in permissions:
                return await call_next(request)

            # ❌ Deny
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
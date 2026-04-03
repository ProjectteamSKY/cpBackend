from app.utils.query_loader import load_queries
from app.core.database import query, execute

queries = load_queries()


async def assign_role_service(ur):
    return await execute(
        queries["user_role"]["assign_role"],
        [ur.user_id, ur.role_id, ur.assigned_by],
        fetch_row=True,
    )


async def get_roles_by_user_service(user_id: int):
    return await query(
        queries["user_role"]["get_roles_by_user"],
        [user_id],
        fetch_all=True,
    )


async def remove_role_service(user_id: int, role_id: int):
    row = await execute(
        queries["user_role"]["remove_role"],
        [user_id, role_id],
        fetch_row=True,
    )
    return bool(row)


async def get_all_users_with_roles_service():
    rows = await query(
        queries["user_role"]["get_all_users_with_roles"],
        fetch_all=True,
    )

    users_dict = {}
    for row in rows:
        user_id = row["id"]
        if user_id not in users_dict:
            users_dict[user_id] = {
                "user_id": user_id,
                "full_name": row["full_name"],
                "email": row["email"],
                "roles": [],
            }
        users_dict[user_id]["roles"].append({
            "role_id": row["role_id"],
            "role_name": row["role_name"],
            "assigned_by": row["assigned_by"],
            "assigned_by_name": row["assigned_by_name"],
            "assigned_at": str(row["assigned_at"]) if row["assigned_at"] else None,
        })

    return list(users_dict.values())
from app.domain.resource_domain import Resource
from app.utils.query_loader import load_queries
from app.core.database import execute, query, query_all

queries = load_queries()


async def create_resource(resource: Resource):
    await execute(
        queries["resource"]["create_resource"],
        {
            "id": resource.id,
            "name": resource.name,
            "description": resource.description,
        },
    )

    return {
        "id": resource.id,
        "name": resource.name,
        "description": resource.description,
    }


async def get_resource_by_name(name: str):
    return await query(
        queries["resource"]["get_by_name"],
        {"name": name},
    )


async def get_resource_by_id(resource_id: str):
    return await query(
        queries["resource"]["get_by_id"],
        {"resource_id": resource_id},
    )


async def get_all_resources():
    return await query_all(
        queries["resource"]["get_all"]
    )


async def delete_resource(resource_id: str):
    result = await execute(
        queries["resource"]["delete_resource"],
        {"resource_id": resource_id},
    )

    return result > 0
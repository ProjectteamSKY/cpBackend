from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import User
from app.repository.user_repository import (
    create_user_repo,
    get_user_by_email_repo
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


async def register_user(data, session: AsyncSession):

    existing = await get_user_by_email_repo(data.email, session)
    if existing:
        return None

    user = User(
        full_name=data.full_name,
        email=data.email,
        contact=data.contact,
        password_hash=hash_password(data.password)
    )

    return await create_user_repo(user, session)


async def login_user(data, session: AsyncSession):
    user = await get_user_by_email_repo(data.email, session)

    if not user:
        return None

    if not verify_password(data.password, user.password_hash):
        return None

    token = create_access_token(user.id)

    # Save token to database
    user.bearer_token = token
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
        "access_token": token,
        "user": user
    }

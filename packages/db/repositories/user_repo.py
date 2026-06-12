from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from packages.db.models import User, AssistantProfile
import uuid

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, name: str,
                     password_hash: str, role: str = "standard") -> User:
        user = User(
            id            = uuid.uuid4(),
            email         = email,
            name          = name,
            role          = role,
            password_hash = password_hash,
            is_active     = True
        )
        self.session.add(user)
        await self.session.flush()
        profile = AssistantProfile(user_id=user.id)
        self.session.add(profile)
        await self.session.commit()
        return user

    async def update_last_seen(self, user_id: str) -> None:
        from sqlalchemy import update
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_seen_at=func.now())
        )
        await self.session.commit()

"""
Seed script — creates default admin user and assistant profile.
Run: docker-compose exec api python -m scripts.seed
"""
import asyncio
from passlib.context import CryptContext
from packages.db.connection import init_db, AsyncSessionFactory
from packages.db.models import User, AssistantProfile
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    await init_db()
    async with AsyncSessionFactory() as session:
        # Check if admin exists
        from sqlalchemy import select
        existing = await session.execute(
            select(User).where(User.email == "admin@aura.local")
        )
        if existing.scalar_one_or_none():
            print("✓ Admin user already exists")
            return

        user = User(
            id            = uuid.uuid4(),
            email         = "admin@aura.local",
            name          = "AURA Admin",
            role          = "admin",
            password_hash = pwd_context.hash("aura_admin_2024"),
            is_active     = True
        )
        session.add(user)
        await session.flush()

        profile = AssistantProfile(
            user_id     = user.id,
            name        = "AURA",
            personality = "friendly",
            wake_phrase = "Hey AURA",
            language    = "en"
        )
        session.add(profile)
        await session.commit()
        print(f"✓ Admin user created: admin@aura.local / aura_admin_2024")
        print(f"  User ID: {user.id}")

if __name__ == "__main__":
    asyncio.run(seed())

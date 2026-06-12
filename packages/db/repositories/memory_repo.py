from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from packages.db.models import MemoryFact
import uuid

class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_facts(self, user_id: str, fact_type: str = None, limit: int = 20) -> list:
        q = select(MemoryFact).where(MemoryFact.user_id == user_id).limit(limit)
        if fact_type:
            q = q.where(MemoryFact.fact_type == fact_type)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def upsert_fact(self, user_id: str, fact_type: str, subject: str,
                          content: str, source: str, confidence: float = 1.0) -> MemoryFact:
        existing = await self.session.execute(
            select(MemoryFact).where(MemoryFact.user_id == user_id)
            .where(MemoryFact.fact_type == fact_type)
            .where(MemoryFact.subject == subject)
        )
        fact = existing.scalar_one_or_none()
        if fact:
            fact.content    = content
            fact.confidence = confidence
        else:
            fact = MemoryFact(id=uuid.uuid4(), user_id=user_id, fact_type=fact_type,
                              subject=subject, content=content, source=source,
                              confidence=confidence)
            self.session.add(fact)
        await self.session.commit()
        return fact

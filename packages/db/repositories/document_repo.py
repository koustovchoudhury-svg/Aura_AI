from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from packages.db.models import Document

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: str) -> list:
        result = await self.session.execute(
            select(Document).where(Document.user_id == user_id)
            .order_by(Document.ingested_at.desc())
        )
        return result.scalars().all()

    async def delete(self, doc_id: str, user_id: str) -> None:
        await self.session.execute(
            delete(Document).where(Document.id == doc_id)
            .where(Document.user_id == user_id)
        )
        await self.session.commit()

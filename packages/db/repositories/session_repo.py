"""Session, AgentRun, Document repositories"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from packages.db.models import Session, Message, AgentRun, Document
import uuid

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, session_id: str, user_id: str,
                            channel: str = "web") -> Session:
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        s = Session(id=session_id, user_id=user_id, channel=channel)
        self.session.add(s)
        await self.session.commit()
        return s

    async def list_by_user(self, user_id: str, limit: int = 20) -> list:
        result = await self.session.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.started_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_messages(self, session_id: str, user_id: str) -> list:
        result = await self.session.execute(
            select(Message)
            .join(Session)
            .where(Message.session_id == session_id)
            .where(Session.user_id == user_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()

    async def save_message(self, session_id: str, role: str,
                           content: str, model: str = None) -> Message:
        msg = Message(
            id=uuid.uuid4(), session_id=session_id,
            role=role, content=content, model_used=model
        )
        self.session.add(msg)
        await self.session.commit()
        return msg


class AgentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, session_id: str, agent_name: str,
                         intent: str, input_data: dict) -> AgentRun:
        run = AgentRun(
            id=uuid.uuid4(), session_id=session_id,
            agent_name=agent_name, intent=intent, input=input_data
        )
        self.session.add(run)
        await self.session.commit()
        return run

    async def complete_run(self, run_id: str, output: dict,
                           status: str = "done") -> None:
        from sqlalchemy import update
        from sqlalchemy.sql import func
        await self.session.execute(
            update(AgentRun)
            .where(AgentRun.id == run_id)
            .values(output=output, status=status,
                    completed_at=func.now())
        )
        await self.session.commit()


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: str) -> list:
        result = await self.session.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.ingested_at.desc())
        )
        return result.scalars().all()

    async def delete(self, doc_id: str, user_id: str) -> None:
        await self.session.execute(
            delete(Document)
            .where(Document.id == doc_id)
            .where(Document.user_id == user_id)
        )
        await self.session.commit()

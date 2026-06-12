from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from packages.db.models import Meeting, MeetingActionItem

class MeetingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: str, limit: int = 20) -> list:
        result = await self.session.execute(
            select(Meeting).where(Meeting.user_id == user_id)
            .order_by(Meeting.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_action_items(self, meeting_id: str) -> list:
        result = await self.session.execute(
            select(MeetingActionItem).where(MeetingActionItem.meeting_id == meeting_id)
        )
        return result.scalars().all()

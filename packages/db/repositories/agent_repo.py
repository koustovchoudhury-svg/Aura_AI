from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql import func
from packages.db.models import AgentRun, ToolCall
import uuid

class AgentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(self, session_id: str, agent_name: str,
                         intent: str, input_data: dict) -> AgentRun:
        run = AgentRun(id=uuid.uuid4(), session_id=session_id,
                       agent_name=agent_name, intent=intent, input=input_data)
        self.session.add(run)
        await self.session.commit()
        return run

    async def complete_run(self, run_id: str, output: dict, status: str = "done") -> None:
        await self.session.execute(
            update(AgentRun).where(AgentRun.id == run_id)
            .values(output=output, status=status, completed_at=func.now())
        )
        await self.session.commit()

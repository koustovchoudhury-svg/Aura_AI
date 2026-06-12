import structlog
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from packages.db.connection import AsyncSessionFactory
from packages.db.models import ScheduledTask, Session, Message
from packages.agents.master.graph import build_master_graph
from packages.agents.master.state import AgentState

log = structlog.get_logger()


class SchedulerManager:
    def __init__(self, registry):
        self.registry  = registry
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.start()
        await self.reload()

    async def shutdown(self):
        self.scheduler.shutdown(wait=False)

    async def reload(self):
        """Reload all enabled scheduled tasks from the DB."""
        for job in list(self.scheduler.get_jobs()):
            job.remove()

        async with AsyncSessionFactory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ScheduledTask).where(ScheduledTask.enabled == True)
            )
            tasks = result.scalars().all()

        for task in tasks:
            self._add_job(task)

    def _add_job(self, task: ScheduledTask):
        try:
            trigger = CronTrigger.from_crontab(task.cron_expr)
        except Exception:
            log.error("scheduler.bad_cron", task_id=str(task.id), cron=task.cron_expr)
            return
        self.scheduler.add_job(
            self.run_task, trigger=trigger,
            id=str(task.id), replace_existing=True,
            args=[str(task.id)]
        )

    async def run_task(self, task_id: str):
        async with AsyncSessionFactory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ScheduledTask).where(ScheduledTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task or not task.enabled:
                return

            user_id = str(task.user_id)

            # Find or create a dedicated "Scheduled Tasks" session for this user
            sess_result = await session.execute(
                select(Session).where(
                    Session.user_id == task.user_id,
                    Session.channel == "scheduler"
                )
            )
            chat_session = sess_result.scalars().first()
            if not chat_session:
                chat_session = Session(
                    user_id=task.user_id, channel="scheduler",
                    title="Scheduled Tasks"
                )
                session.add(chat_session)
                await session.commit()

            session_id = str(chat_session.id)

        try:
            graph  = build_master_graph(registry=self.registry)
            state  = AgentState(
                user_input=task.instruction,
                user_id=user_id,
                session_id=session_id,
                # Scheduled tasks were pre-approved by the user when created
                approval_granted=True
            )
            config = {"configurable": {"thread_id": f"sched_{task_id}_{datetime.utcnow().timestamp()}"}}
            final_state = await graph.ainvoke(state.model_dump(), config)
            output = final_state.get("final_response", "") if isinstance(final_state, dict) else ""
        except Exception as e:
            output = f"Scheduled task failed: {e}"
            log.error("scheduler.run_failed", task_id=task_id, error=str(e))

        async with AsyncSessionFactory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ScheduledTask).where(ScheduledTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if task:
                task.last_run_at = datetime.utcnow()
                task.last_result = output[:4000]

            session.add(Message(
                session_id=session_id, role="user",
                content=f"⏰ [Scheduled: {task.name if task else task_id}] {task.instruction if task else ''}"
            ))
            session.add(Message(
                session_id=session_id, role="assistant", content=output
            ))
            await session.commit()

        log.info("scheduler.run_complete", task_id=task_id)

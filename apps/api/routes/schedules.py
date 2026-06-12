from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from packages.db.connection import get_session
from packages.db.models import ScheduledTask
from .auth import get_current_user

router = APIRouter()


class ScheduleCreate(BaseModel):
    name: str
    cron_expr: str
    instruction: str
    enabled: bool = True


class ScheduleUpdate(BaseModel):
    name: str | None = None
    cron_expr: str | None = None
    instruction: str | None = None
    enabled: bool | None = None


def _serialize(t: ScheduledTask) -> dict:
    return {
        "id": str(t.id),
        "name": t.name,
        "cron_expr": t.cron_expr,
        "instruction": t.instruction,
        "enabled": t.enabled,
        "last_run_at": str(t.last_run_at) if t.last_run_at else None,
        "last_result": t.last_result,
        "created_at": str(t.created_at),
    }


@router.get("")
async def list_schedules(user=Depends(get_current_user), session=Depends(get_session)):
    result = await session.execute(
        select(ScheduledTask).where(ScheduledTask.user_id == user.id)
        .order_by(ScheduledTask.created_at.desc())
    )
    return {"schedules": [_serialize(t) for t in result.scalars().all()]}


@router.post("")
async def create_schedule(
    data: ScheduleCreate, request: Request,
    user=Depends(get_current_user), session=Depends(get_session)
):
    try:
        from apscheduler.triggers.cron import CronTrigger
        CronTrigger.from_crontab(data.cron_expr)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cron expression")

    task = ScheduledTask(
        user_id=user.id, name=data.name, cron_expr=data.cron_expr,
        instruction=data.instruction, enabled=data.enabled
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    sched = getattr(request.app.state, "scheduler", None)
    if sched:
        await sched.reload()

    return _serialize(task)


@router.patch("/{schedule_id}")
async def update_schedule(
    schedule_id: str, data: ScheduleUpdate, request: Request,
    user=Depends(get_current_user), session=Depends(get_session)
):
    result = await session.execute(
        select(ScheduledTask).where(
            ScheduledTask.id == schedule_id, ScheduledTask.user_id == user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if data.cron_expr is not None:
        try:
            from apscheduler.triggers.cron import CronTrigger
            CronTrigger.from_crontab(data.cron_expr)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cron expression")
        task.cron_expr = data.cron_expr
    if data.name is not None:
        task.name = data.name
    if data.instruction is not None:
        task.instruction = data.instruction
    if data.enabled is not None:
        task.enabled = data.enabled

    await session.commit()
    await session.refresh(task)

    sched = getattr(request.app.state, "scheduler", None)
    if sched:
        await sched.reload()

    return _serialize(task)


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str, request: Request,
    user=Depends(get_current_user), session=Depends(get_session)
):
    result = await session.execute(
        select(ScheduledTask).where(
            ScheduledTask.id == schedule_id, ScheduledTask.user_id == user.id
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await session.delete(task)
    await session.commit()

    sched = getattr(request.app.state, "scheduler", None)
    if sched:
        await sched.reload()

    return {"status": "deleted"}

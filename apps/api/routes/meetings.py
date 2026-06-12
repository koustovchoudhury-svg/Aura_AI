import os, uuid
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy import select, update
from packages.db.connection import get_session, AsyncSessionFactory
from packages.db.models import Meeting
from packages.voice.stt import transcribe_file
from packages.agents.meeting.agent import MeetingAgent
from packages.agents.master.state import TaskItem
from packages.agents.base.agent import AgentContext
from .auth import get_current_user

router = APIRouter()
agent  = MeetingAgent()

@router.post("/upload")
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    upload_dir = "/tmp/aura_meetings"
    os.makedirs(upload_dir, exist_ok=True)
    file_path  = f"{upload_dir}/{uuid.uuid4()}_{file.filename}"
    with open(file_path,"wb") as f: f.write(await file.read())
    meeting = Meeting(id=uuid.uuid4(), user_id=user.id,
                      title=file.filename, audio_path=file_path)
    session.add(meeting)
    await session.commit()
    background_tasks.add_task(process_meeting, str(meeting.id), file_path, str(user.id))
    return {"status":"processing","meeting_id":str(meeting.id)}

async def process_meeting(meeting_id: str, file_path: str, user_id: str):
    result = await transcribe_file(file_path)
    task   = TaskItem(id="m1", description="Analyse meeting",
                      agent="MeetingAgent",
                      metadata={"transcript": result["transcript"]})
    ctx    = AgentContext(user_id=user_id)
    ar     = await agent.execute(task, ctx)
    async with AsyncSessionFactory() as s:
        vals = {"transcript": result["transcript"]}
        if ar.success and ar.output:
            vals.update({"summary": ar.output.get("summary",""),
                         "decisions": ar.output.get("decisions",[]),
                         "key_topics": ar.output.get("key_topics",[])})
        await s.execute(update(Meeting).where(Meeting.id == meeting_id).values(**vals))
        await s.commit()

@router.get("/")
async def list_meetings(user=Depends(get_current_user), session=Depends(get_session)):
    result = await session.execute(
        select(Meeting).where(Meeting.user_id == str(user.id))
        .order_by(Meeting.created_at.desc())
    )
    meetings = result.scalars().all()
    return {"meetings": [
        {"id":str(m.id),"title":m.title,"platform":m.platform,
         "summary":m.summary,"created_at":str(m.created_at)}
        for m in meetings
    ]}

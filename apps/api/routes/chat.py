import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request
from packages.agents.master.graph import build_master_graph
from packages.agents.master.state import AgentState
from packages.db.connection import get_session
from .auth import get_current_user

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str,
                         token: str = "", request: Request = None):
    await websocket.accept()
    try:
        registry = websocket.app.state.registry
    except Exception:
        await websocket.send_json({"type":"error","message":"Registry not ready"})
        return

    graph = build_master_graph(registry=registry)

    try:
        async for raw in websocket.iter_text():
            data = json.loads(raw)
            if data.get("type") == "approval_response":
                config = {"configurable":{"thread_id":session_id}}
                graph.update_state(config,{"approval_granted":data.get("approved",False)})
                continue

            state  = AgentState(
                user_input = data.get("message",""),
                user_id    = data.get("user_id",""),
                session_id = session_id
            )
            config = {"configurable":{"thread_id":session_id}}

            async for event in graph.astream_events(state.model_dump(), config, version="v2"):
                etype = event.get("event","")
                if etype == "on_chat_model_stream" and event.get("metadata", {}).get("langgraph_node") == "validator":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        await websocket.send_json({"type":"token","content":chunk})
                elif etype == "on_node_start":
                    await websocket.send_json({"type":"status","node":event.get("name","")})

            await websocket.send_json({"type":"done"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type":"error","message":str(e)})

@router.get("/sessions")
async def list_sessions(user=Depends(get_current_user), session=Depends(get_session)):
    from sqlalchemy import select
    from packages.db.models import Session
    result = await session.execute(
        select(Session).where(Session.user_id == str(user.id))
        .order_by(Session.started_at.desc()).limit(50)
    )
    sessions = result.scalars().all()
    return {"sessions": [
        {"id":str(s.id),"title":s.title,"channel":s.channel,"started_at":str(s.started_at)}
        for s in sessions
    ]}

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, user=Depends(get_current_user), session=Depends(get_session)):
    from sqlalchemy import select
    from packages.db.models import Session, Message
    try:
        sess = await session.get(Session, session_id)
    except Exception:
        return {"messages": []}
    if not sess or str(sess.user_id) != str(user.id):
        return {"messages": []}
    result = await session.execute(
        select(Message).where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    return {"messages": [
        {"id":str(m.id),"role":m.role,"content":m.content,"created_at":str(m.created_at)}
        for m in result.scalars().all()
    ]}

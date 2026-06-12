from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from packages.db.connection import get_session
from packages.db.models import IntegrationToken, MemoryFact, AssistantProfile
from .auth import get_current_user

router = APIRouter()

# ── Connectors (integration_tokens) ─────────────────────────────────
SUPPORTED_PLATFORMS = ["slack", "github", "jira", "email", "google_calendar"]

class ConnectorCreate(BaseModel):
    platform: str
    access_token: str
    refresh_token: str | None = None
    workspace_id: str | None = None
    scopes: list[str] = []

def _serialize_connector(t: IntegrationToken) -> dict:
    return {
        "id": str(t.id), "platform": t.platform,
        "workspace_id": t.workspace_id, "scopes": t.scopes,
        "connected_at": str(t.created_at),
        "token_preview": (t.access_token[:4] + "..." + t.access_token[-4:]) if len(t.access_token) > 8 else "****",
    }

@router.get("/connectors")
async def list_connectors(user=Depends(get_current_user), session=Depends(get_session)):
    result = await session.execute(
        select(IntegrationToken).where(IntegrationToken.user_id == user.id)
    )
    connected = {t.platform: _serialize_connector(t) for t in result.scalars().all()}
    return {
        "connectors": [
            {"platform": p, "connected": p in connected, **connected.get(p, {})}
            for p in SUPPORTED_PLATFORMS
        ]
    }

@router.post("/connectors")
async def connect_platform(data: ConnectorCreate, user=Depends(get_current_user), session=Depends(get_session)):
    if data.platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform. Choose one of: {SUPPORTED_PLATFORMS}")
    result = await session.execute(
        select(IntegrationToken).where(
            IntegrationToken.user_id == user.id,
            IntegrationToken.platform == data.platform
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.access_token = data.access_token
        existing.refresh_token = data.refresh_token
        existing.workspace_id = data.workspace_id
        existing.scopes = data.scopes
        existing.updated_at = datetime.utcnow()
    else:
        session.add(IntegrationToken(
            user_id=user.id, platform=data.platform,
            access_token=data.access_token, refresh_token=data.refresh_token,
            workspace_id=data.workspace_id, scopes=data.scopes
        ))
    await session.commit()
    return {"status": "connected", "platform": data.platform}

@router.delete("/connectors/{platform}")
async def disconnect_platform(platform: str, user=Depends(get_current_user), session=Depends(get_session)):
    result = await session.execute(
        select(IntegrationToken).where(
            IntegrationToken.user_id == user.id,
            IntegrationToken.platform == platform
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        await session.delete(existing)
        await session.commit()
    return {"status": "disconnected", "platform": platform}


# ── Memory facts ─────────────────────────────────────────────────────
class MemoryFactCreate(BaseModel):
    fact_type: str = "note"
    subject: str | None = None
    content: str

def _serialize_fact(f: MemoryFact) -> dict:
    return {
        "id": str(f.id), "fact_type": f.fact_type, "subject": f.subject,
        "content": f.content, "source": f.source, "confidence": f.confidence,
        "created_at": str(f.created_at),
    }

@router.get("/memory")
async def list_memory(user=Depends(get_current_user), session=Depends(get_session)):
    result = await session.execute(
        select(MemoryFact).where(MemoryFact.user_id == user.id)
        .order_by(MemoryFact.created_at.desc()).limit(200)
    )
    return {"facts": [_serialize_fact(f) for f in result.scalars().all()]}

@router.post("/memory")
async def add_memory(data: MemoryFactCreate, user=Depends(get_current_user), session=Depends(get_session)):
    fact = MemoryFact(
        user_id=user.id, fact_type=data.fact_type, subject=data.subject,
        content=data.content, source="user", confidence=1.0
    )
    session.add(fact)
    await session.commit()
    return _serialize_fact(fact)

@router.delete("/memory/{fact_id}")
async def delete_memory(fact_id: str, user=Depends(get_current_user), session=Depends(get_session)):
    result = await session.execute(
        select(MemoryFact).where(MemoryFact.id == fact_id, MemoryFact.user_id == user.id)
    )
    fact = result.scalar_one_or_none()
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    await session.delete(fact)
    await session.commit()
    return {"status": "deleted"}


# ── Skill toggles (per-agent enabled tools, stored on assistant_profiles.preferences) ──
class SkillsUpdate(BaseModel):
    disabled_tools: list[str] = []

async def _get_profile(user, session) -> AssistantProfile:
    result = await session.execute(
        select(AssistantProfile).where(AssistantProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = AssistantProfile(user_id=user.id, preferences={})
        session.add(profile)
        await session.commit()
    return profile

@router.get("/skills")
async def get_skills(user=Depends(get_current_user), session=Depends(get_session)):
    profile = await _get_profile(user, session)
    return {"disabled_tools": profile.preferences.get("disabled_tools", [])}

@router.put("/skills")
async def update_skills(data: SkillsUpdate, user=Depends(get_current_user), session=Depends(get_session)):
    profile = await _get_profile(user, session)
    prefs = dict(profile.preferences or {})
    prefs["disabled_tools"] = data.disabled_tools
    profile.preferences = prefs
    profile.updated_at = datetime.utcnow()
    await session.commit()
    return {"disabled_tools": profile.preferences["disabled_tools"]}

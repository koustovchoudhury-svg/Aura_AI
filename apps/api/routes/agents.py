from fastapi import APIRouter, Request, Depends
from .auth import get_current_user

router = APIRouter()

@router.get("/")
async def list_agents(request: Request, user=Depends(get_current_user)):
    registry = request.app.state.registry
    return {"agents": [
        {
            "name": m.name, "description": m.description, "intents": m.intents,
            "enabled": m.enabled, "tags": m.tags,
            "tools": [
                {"name": t.name, "description": t.description,
                 "permission": t.permission.value, "cost_tier": t.cost_tier.value}
                for t in m.tools
            ]
        }
        for m in registry.list_all()
    ]}

@router.get("/health")
async def agents_health(request: Request, user=Depends(get_current_user)):
    registry = request.app.state.registry
    return {"health": await registry.health_check_all()}

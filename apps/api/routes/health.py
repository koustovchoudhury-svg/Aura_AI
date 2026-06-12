from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health(request: Request):
    try:
        registry = request.app.state.registry
        agents   = await registry.health_check_all()
    except Exception:
        agents = {}
    return {"status":"healthy","timestamp":datetime.utcnow().isoformat(),
            "version":"1.0.0","agents":agents}

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app

from packages.db.connection import init_db
from packages.agents.registry import AgentRegistry, bootstrap_registry
from packages.rag.vector_store import VectorStore
from config import settings

log = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("aura.startup", version="1.0.0")
    await init_db()
    registry = AgentRegistry()
    await bootstrap_registry(registry)
    app.state.registry = registry
    qdrant = VectorStore(url=settings.QDRANT_URL)
    await qdrant.init_collection()
    app.state.qdrant = qdrant

    from packages.scheduler.manager import SchedulerManager
    scheduler = SchedulerManager(registry)
    await scheduler.start()
    app.state.scheduler = scheduler

    log.info("aura.ready")
    yield
    await scheduler.shutdown()
    log.info("aura.shutdown")

app = FastAPI(
    title="AURA AI-OS API",
    version="1.0.0",
    description="Autonomous Unified Responsive Assistant",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

from routes.auth      import router as auth_router
from routes.chat      import router as chat_router
from routes.agents    import router as agents_router
from routes.knowledge import router as knowledge_router
from routes.meetings  import router as meetings_router
from routes.health    import router as health_router
from routes.voice     import router as voice_router
from routes.schedules import router as schedules_router
from routes.settings  import router as settings_router

app.include_router(auth_router,      prefix="/api/auth",      tags=["auth"])
app.include_router(chat_router,      prefix="/api/chat",      tags=["chat"])
app.include_router(agents_router,    prefix="/api/agents",    tags=["agents"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(meetings_router,  prefix="/api/meetings",  tags=["meetings"])
app.include_router(health_router,    prefix="/api",           tags=["health"])
app.include_router(voice_router,     prefix="/api/voice",      tags=["voice"])
app.include_router(schedules_router, prefix="/api/schedules",  tags=["schedules"])
app.include_router(settings_router,  prefix="/api/settings",  tags=["settings"])

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# AURA AI-OS — Claude Code Master Build File
# Version: 1.0 | Author: Solution Architecture Team
# ════════════════════════════════════════════════════════════════════
# HOW TO USE THIS FILE
# ════════════════════════════════════════════════════════════════════
# This file contains the COMPLETE blueprint for building AURA AI-OS.
# Claude Code reads this file and executes builds phase by phase.
#
# USAGE IN VS CODE:
#   1. Open this folder in VS Code with Claude Code extension
#   2. Say: "Read CLAUDE.md and start Phase 1"
#   3. Claude Code will create ALL files, install deps, run migrations
#   4. After each phase: "Continue with Phase N"
#
# DO NOT SKIP PHASES — each phase depends on the previous.
# ════════════════════════════════════════════════════════════════════

## PROJECT IDENTITY
- Name: AURA AI-OS (Autonomous Unified Responsive Assistant)
- Stack: Python 3.11 / FastAPI / LangGraph / Next.js 14 / PostgreSQL / Qdrant / Redis
- Pattern: Master Agent + Dynamic Sub-Agent Composition (Option B)
- Deployment: Docker Compose (dev) → Docker Swarm (team) → Kubernetes (enterprise)

## MONOREPO STRUCTURE TO CREATE
```
D:\Project\Aura AI\
├── CLAUDE.md                    ← this file
├── .env.example
├── .env                         ← copy from .env.example, fill secrets
├── docker-compose.yml
├── docker-compose.prod.yml
├── pyproject.toml
├── Makefile
│
├── apps/
│   ├── api/                     ← FastAPI backend
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── chat.py
│   │       ├── agents.py
│   │       ├── knowledge.py
│   │       ├── meetings.py
│   │       ├── auth.py
│   │       └── health.py
│   │
│   └── frontend/                ← Next.js 14
│       ├── Dockerfile
│       ├── package.json
│       ├── next.config.js
│       ├── tailwind.config.js
│       └── src/
│           ├── app/
│           │   ├── layout.tsx
│           │   ├── page.tsx
│           │   └── chat/
│           │       └── page.tsx
│           ├── components/
│           │   ├── chat/
│           │   ├── voice/
│           │   └── ui/
│           └── lib/
│               ├── api.ts
│               └── websocket.ts
│
├── packages/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── manifest.py
│   │   ├── master/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py
│   │   │   ├── nodes.py
│   │   │   └── state.py
│   │   ├── personal/
│   │   ├── meeting/
│   │   ├── coding/
│   │   ├── devops/
│   │   ├── communication/
│   │   └── marketing/
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── processor.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── worker.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── user_repo.py
│   │       ├── session_repo.py
│   │       ├── agent_repo.py
│   │       ├── memory_repo.py
│   │       ├── document_repo.py
│   │       └── meeting_repo.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   ├── memory.py
│   │   ├── slack.py
│   │   ├── jira.py
│   │   ├── github.py
│   │   ├── kubectl.py
│   │   └── email_tool.py
│   │
│   └── voice/
│       ├── __init__.py
│       ├── stt.py
│       └── tts.py
│
├── infrastructure/
│   ├── nginx/
│   │   └── nginx.conf
│   ├── postgres/
│   │   └── init.sql
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana/
│
└── migrations/
    ├── env.py
    ├── alembic.ini
    └── versions/
        └── 001_initial_schema.sql
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 1 — INFRASTRUCTURE & PROJECT SCAFFOLD
## Command to Claude Code: "Build Phase 1"
## ════════════════════════════════════════════════════════════════════

### STEP 1.1 — Create .env.example
```
# ── LLM ──────────────────────────────────────────────────────
OLLAMA_BASE_URL=http://ollama:11434
LITELLM_BASE_URL=http://litellm:8080
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_LOCAL_MODEL=llama3.2:3b
DEFAULT_CLOUD_MODEL=claude-sonnet-4-6
EMBED_MODEL=nomic-embed-text

# ── Database ──────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://aura:aura_secret@postgres:5432/aura_db
POSTGRES_USER=aura
POSTGRES_PASSWORD=aura_secret
POSTGRES_DB=aura_db

# ── Vector DB ─────────────────────────────────────────────────
QDRANT_URL=http://qdrant:6333

# ── Cache ─────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── Queue ─────────────────────────────────────────────────────
RABBITMQ_URL=amqp://aura:aura_secret@rabbitmq:5672/
RABBITMQ_USER=aura
RABBITMQ_PASSWORD=aura_secret

# ── Storage ───────────────────────────────────────────────────
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=aura_minio
MINIO_SECRET_KEY=aura_minio_secret
MINIO_BUCKET=aura-files

# ── Auth ──────────────────────────────────────────────────────
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=aura
KEYCLOAK_CLIENT_ID=aura-api
KEYCLOAK_CLIENT_SECRET=your-client-secret
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# ── API ───────────────────────────────────────────────────────
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ── Frontend ──────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### STEP 1.2 — Create docker-compose.yml
```yaml
version: "3.9"

services:
  # ── Infrastructure ────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"

  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
              count: all

  # ── Application ───────────────────────────────────────────────
  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - QDRANT_URL=${QDRANT_URL}
      - RABBITMQ_URL=${RABBITMQ_URL}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./apps/api:/app
      - ./packages:/app/packages
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  rag_worker:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - QDRANT_URL=${QDRANT_URL}
      - RABBITMQ_URL=${RABBITMQ_URL}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
    volumes:
      - ./apps/api:/app
      - ./packages:/app/packages
    depends_on:
      - api
    command: python -m packages.rag.worker

  frontend:
    build:
      context: ./apps/frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}
    volumes:
      - ./apps/frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - api
    command: npm run dev

  nginx:
    image: nginx:alpine
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - api
      - frontend

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  rabbitmq_data:
  minio_data:
  ollama_data:
```

### STEP 1.3 — Create Makefile
```makefile
.PHONY: help up down build migrate seed pull-models logs clean

help:
	@echo "AURA AI-OS — Available commands"
	@echo "  make up           Start all services"
	@echo "  make down         Stop all services"
	@echo "  make build        Build docker images"
	@echo "  make migrate      Run database migrations"
	@echo "  make seed         Seed initial data"
	@echo "  make pull-models  Pull Ollama models"
	@echo "  make logs         Tail all logs"
	@echo "  make clean        Remove all volumes (destructive)"

up:
	docker-compose up -d
	@echo "✓ AURA AI-OS running"
	@echo "  API:      http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  RabbitMQ: http://localhost:15672"
	@echo "  MinIO:    http://localhost:9001"

down:
	docker-compose down

build:
	docker-compose build --no-cache

migrate:
	docker-compose exec api alembic upgrade head

seed:
	docker-compose exec api python -m scripts.seed

pull-models:
	docker-compose exec ollama ollama pull llama3.2:3b
	docker-compose exec ollama ollama pull mistral:7b
	docker-compose exec ollama ollama pull nomic-embed-text
	docker-compose exec ollama ollama pull qwen2.5:7b

logs:
	docker-compose logs -f --tail=100

clean:
	docker-compose down -v
	@echo "⚠ All volumes removed"

test:
	docker-compose exec api pytest packages/ -v

format:
	docker-compose exec api black packages/ apps/api/
	docker-compose exec api ruff packages/ apps/api/
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 2 — BACKEND API (FastAPI)
## Command to Claude Code: "Build Phase 2"
## ════════════════════════════════════════════════════════════════════

### STEP 2.1 — apps/api/requirements.txt
```
# Core
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.8.0
pydantic-settings==2.4.0
python-multipart==0.0.9

# Database
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
alembic==1.13.2
psycopg2-binary==2.9.9

# Cache
redis[hiredis]==5.0.8
aioredis==2.0.1

# Queue
aio-pika==9.4.3

# Vector DB
qdrant-client==1.11.0

# LLM & Agents
langchain==0.3.0
langchain-community==0.3.0
langgraph==0.2.28
langchain-openai==0.2.0
langchain-anthropic==0.2.0
litellm==1.48.0
openai==1.51.0
anthropic==0.34.0

# RAG
sentence-transformers==3.1.0
rank-bm25==0.2.2
pymupdf4llm==0.0.17
mammoth==1.8.0
pandas==2.2.3
openpyxl==3.1.5
nltk==3.9.1

# Voice
faster-whisper==1.0.3

# Storage
minio==7.2.8

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.2

# Utils
python-dotenv==1.0.1
structlog==24.4.0
prometheus-client==0.21.0
tenacity==9.0.0
```

### STEP 2.2 — apps/api/Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

COPY . .

ENV PYTHONPATH=/app:/app/packages

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### STEP 2.3 — apps/api/main.py
```python
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app

from packages.db.connection import init_db
from packages.agents.registry import AgentRegistry, bootstrap_registry
from packages.rag.vector_store import VectorStore
from routes import chat, agents, knowledge, meetings, auth, health
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
    log.info("aura.ready")
    yield
    log.info("aura.shutdown")

app = FastAPI(
    title="AURA AI-OS API",
    version="1.0.0",
    description="Autonomous Unified Responsive Assistant",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routes
app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(chat.router,      prefix="/api/chat",      tags=["chat"])
app.include_router(agents.router,    prefix="/api/agents",    tags=["agents"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(meetings.router,  prefix="/api/meetings",  tags=["meetings"])
app.include_router(health.router,    prefix="/api",           tags=["health"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### STEP 2.4 — apps/api/config.py
```python
from pydantic_settings import BaseSettings
from typing import list

class Settings(BaseSettings):
    # LLM
    OLLAMA_BASE_URL:       str = "http://ollama:11434"
    OPENAI_API_KEY:        str = ""
    ANTHROPIC_API_KEY:     str = ""
    DEFAULT_LOCAL_MODEL:   str = "llama3.2:3b"
    DEFAULT_CLOUD_MODEL:   str = "claude-sonnet-4-6"
    EMBED_MODEL:           str = "nomic-embed-text"

    # Database
    DATABASE_URL:          str = "postgresql+asyncpg://aura:aura_secret@postgres:5432/aura_db"

    # Services
    QDRANT_URL:            str = "http://qdrant:6333"
    REDIS_URL:             str = "redis://redis:6379/0"
    RABBITMQ_URL:          str = "amqp://aura:aura_secret@rabbitmq:5672/"

    # Storage
    MINIO_ENDPOINT:        str = "minio:9000"
    MINIO_ACCESS_KEY:      str = "aura_minio"
    MINIO_SECRET_KEY:      str = "aura_minio_secret"
    MINIO_BUCKET:          str = "aura-files"

    # Auth
    JWT_SECRET:            str = "change-me-in-production"
    JWT_ALGORITHM:         str = "HS256"
    JWT_EXPIRE_MINUTES:    int = 1440

    # API
    API_HOST:              str = "0.0.0.0"
    API_PORT:              int = 8000
    API_DEBUG:             bool = True
    CORS_ORIGINS:          list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra    = "ignore"

settings = Settings()
```

### STEP 2.5 — apps/api/routes/auth.py
```python
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from packages.db.connection import get_session
from packages.db.repositories.user_repo import UserRepository
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class Token(BaseModel):
    access_token: str
    token_type:   str
    user_id:      str
    name:         str

class UserCreate(BaseModel):
    email:    str
    name:     str
    password: str

class UserOut(BaseModel):
    id:         str
    email:      str
    name:       str
    role:       str
    created_at: datetime

def create_token(user_id: str, email: str) -> str:
    expire  = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session=Depends(get_session)
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", response_model=UserOut)
async def register(data: UserCreate, session=Depends(get_session)):
    repo = UserRepository(session)
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(data.password)
    user   = await repo.create(data.email, data.name, hashed)
    return user

@router.post("/token", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session)
):
    repo = UserRepository(session)
    user = await repo.get_by_email(form.username)
    if not user or not pwd_context.verify(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(user.id), user.email)
    return Token(access_token=token, token_type="bearer",
                 user_id=str(user.id), name=user.name)
```

### STEP 2.6 — apps/api/routes/chat.py
```python
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse

from packages.agents.master.graph import build_master_graph
from packages.agents.master.state import AgentState
from packages.db.connection import get_session
from packages.db.repositories.session_repo import SessionRepository
from packages.db.repositories.agent_repo import AgentRepository
from .auth import get_current_user

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str,
    request: Request
):
    await websocket.accept()
    registry = request.app.state.registry

    try:
        graph = build_master_graph(registry=registry)

        async for raw in websocket.iter_text():
            data = json.loads(raw)

            # Handle approval responses
            if data.get("type") == "approval_response":
                config = {"configurable": {"thread_id": session_id}}
                graph.update_state(config, {
                    "approval_granted": data["approved"],
                    "approval_responded": True
                })
                await graph.ainvoke(None, config)
                continue

            # Normal message
            state = AgentState(
                user_input  = data["message"],
                user_id     = data["user_id"],
                session_id  = session_id
            )
            config = {"configurable": {"thread_id": session_id}}

            async for event in graph.astream_events(state, config, version="v2"):
                event_type = event.get("event", "")

                if event_type == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        await websocket.send_json({
                            "type": "token", "content": chunk
                        })

                elif event_type == "on_node_start":
                    node = event.get("name", "")
                    await websocket.send_json({
                        "type": "status", "node": node
                    })

            # Signal completion
            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})

@router.get("/sessions")
async def list_sessions(
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    repo   = SessionRepository(session)
    result = await repo.list_by_user(str(user.id), limit=20)
    return result

@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    repo = SessionRepository(session)
    return await repo.get_messages(session_id, str(user.id))
```

### STEP 2.7 — apps/api/routes/knowledge.py
```python
import os
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel

from packages.rag.engine import RAGEngine
from packages.db.connection import get_session
from packages.db.repositories.document_repo import DocumentRepository
from .auth import get_current_user

router  = APIRouter()
rag_engine = RAGEngine()

class QueryRequest(BaseModel):
    query:   str
    top_k:   int = 5
    filters: dict = {}

@router.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    upload_dir = "/tmp/aura_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    background_tasks.add_task(
        rag_engine.ingest, file_path, str(user.id)
    )
    return {"status": "queued", "filename": file.filename}

@router.post("/query")
async def query_knowledge(
    req: QueryRequest,
    user=Depends(get_current_user)
):
    chunks = await rag_engine.retrieve(
        query   = req.query,
        user_id = str(user.id),
        top_k   = req.top_k
    )
    return {"results": chunks}

@router.get("/documents")
async def list_documents(
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    repo = DocumentRepository(session)
    return await repo.list_by_user(str(user.id))

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    user=Depends(get_current_user),
    session=Depends(get_session)
):
    repo = DocumentRepository(session)
    await repo.delete(doc_id, str(user.id))
    await rag_engine.store.delete_by_doc_id(doc_id)
    return {"status": "deleted"}
```

### STEP 2.8 — apps/api/routes/health.py
```python
from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health(request: Request):
    registry = request.app.state.registry
    agents   = await registry.health_check_all()
    return {
        "status":    "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version":   "1.0.0",
        "agents":    agents
    }
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 3 — AGENT SYSTEM
## Command to Claude Code: "Build Phase 3"
## ════════════════════════════════════════════════════════════════════

### STEP 3.1 — packages/agents/base/manifest.py
```python
from enum import Enum
from pydantic import BaseModel

class PermissionLevel(str, Enum):
    READ_ONLY         = "read_only"
    APPROVAL_REQUIRED = "approval_required"
    AUTONOMOUS        = "autonomous"

class CostTier(str, Enum):
    FREE   = "free"
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"

class ToolManifest(BaseModel):
    name:            str
    description:     str
    permission:      PermissionLevel = PermissionLevel.READ_ONLY
    cost_tier:       CostTier = CostTier.FREE
    input_schema:    dict = {}
    output_schema:   dict = {}
    timeout_seconds: int = 30

class AgentManifest(BaseModel):
    name:                 str
    version:              str = "1.0.0"
    description:          str
    intents:              list[str]
    keywords:             list[str]
    tools:                list[ToolManifest] = []
    requires_llm:         bool = True
    preferred_model:      str = "auto"
    max_parallel:         int = 3
    timeout_seconds:      int = 120
    max_permission:       PermissionLevel = PermissionLevel.APPROVAL_REQUIRED
    confidence_threshold: float = 0.7
    enabled:              bool = True
    tags:                 list[str] = []
```

### STEP 3.2 — packages/agents/base/agent.py
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from .manifest import AgentManifest, ToolManifest

@dataclass
class AgentContext:
    session_context:  list[dict] = field(default_factory=list)
    long_term_facts:  list[str]  = field(default_factory=list)
    rag_chunks:       list[str]  = field(default_factory=list)
    user_id:          str = ""
    session_id:       str = ""

@dataclass
class AgentResult:
    success:     bool
    output:      Any
    tool_calls:  list[dict] = field(default_factory=list)
    tokens_used: int   = 0
    cost_usd:    float = 0.0
    error:       str   = ""
    metadata:    dict  = field(default_factory=dict)

class BaseAgent(ABC):
    manifest: AgentManifest

    @abstractmethod
    async def execute(self, task: Any, context: AgentContext) -> AgentResult:
        ...

    def can_handle(self, intent: str) -> float:
        if intent in self.manifest.intents:
            return 1.0
        matches = sum(1 for k in self.manifest.keywords
                      if k.lower() in intent.lower())
        return min(matches / max(len(self.manifest.keywords), 1), 0.9)

    async def health_check(self) -> bool:
        return self.manifest.enabled

    def get_tools(self) -> list[ToolManifest]:
        return self.manifest.tools

    def get_cost_estimate(self, tools: list[str]) -> float:
        tier_map = {"free": 0.0, "low": 0.005, "medium": 0.05, "high": 0.20}
        return sum(
            tier_map.get(t.cost_tier, 0.0)
            for t in self.manifest.tools if t.name in tools
        )

    def _build_system_prompt(self, context: AgentContext) -> str:
        facts   = "\n".join(context.long_term_facts)
        chunks  = "\n\n".join(context.rag_chunks)
        history = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in context.session_context[-6:]
        ])
        return f"""You are {self.manifest.name}.
Role: {self.manifest.description}

## User context
{facts}

## Relevant knowledge
{chunks}

## Recent conversation
{history}

Be concise, precise, and action-oriented."""
```

### STEP 3.3 — packages/agents/master/state.py
```python
from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

class TaskItem(BaseModel):
    id:          str
    description: str
    agent:       str
    tools:       list[str] = []
    depends_on:  list[str] = []
    status:      Literal["pending","running","done","failed"] = "pending"
    result:      Any = None
    metadata:    dict = {}

class AgentState(BaseModel):
    # Input
    user_input: str
    user_id:    str = ""
    session_id: str = ""

    # Intent
    intent:            str   = ""
    intent_confidence: float = 0.0
    subtasks:          list[TaskItem] = []

    # Memory
    session_context: list[dict] = []
    long_term_facts: list[str]  = []
    rag_chunks:      list[str]  = []

    # Execution control
    requires_approval:   bool = False
    approval_granted:    bool = False
    approval_reason:     str  = ""
    approval_responded:  bool = False
    retry_count:         int  = 0
    max_retries:         int  = 3

    # Output
    agent_results:    dict[str, Any] = {}
    final_response:   str  = ""
    validation_passed: bool = False

    # Conversation
    messages: Annotated[list, add_messages] = []
```

### STEP 3.4 — packages/agents/master/nodes.py
```python
import asyncio
import json
from langchain_core.messages import SystemMessage, HumanMessage

from packages.agents.master.state import AgentState, TaskItem
from packages.agents.base.agent import AgentContext

RISKY_TOOLS = {
    "kubectl_delete", "kubectl_apply", "terraform_apply",
    "send_email", "post_slack", "post_telegram",
    "create_jira", "aws_terminate", "github_merge"
}

# ── Intent Classifier ──────────────────────────────────────────────
async def intent_classifier(state: AgentState, llm) -> dict:
    prompt = f"""Classify this request. Return ONLY valid JSON.

Request: {state.user_input}

Return:
{{
  "intent": "personal|meeting|coding|devops|communication|marketing|research",
  "confidence": 0.95,
  "subtasks": [
    {{
      "id": "t1",
      "description": "specific task description",
      "agent": "PersonalAssistantAgent",
      "tools": ["tool_name"],
      "depends_on": []
    }}
  ]
}}"""
    response = await llm.ainvoke([
        SystemMessage(content="You are a task classifier. Return only JSON."),
        HumanMessage(content=prompt)
    ])
    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw.strip())
        return {
            "intent":            parsed.get("intent", "personal"),
            "intent_confidence": parsed.get("confidence", 0.8),
            "subtasks": [
                TaskItem(**t) for t in parsed.get("subtasks", [])
            ]
        }
    except Exception:
        return {
            "intent": "personal",
            "intent_confidence": 0.5,
            "subtasks": [TaskItem(
                id="t1",
                description=state.user_input,
                agent="PersonalAssistantAgent",
                tools=[]
            )]
        }

# ── Planner ───────────────────────────────────────────────────────
async def planner(state: AgentState, registry) -> dict:
    tasks = state.subtasks
    for task in tasks:
        if not registry.has(task.agent):
            task.agent = registry.best_match(task.description)
    return {"subtasks": tasks}

# ── Memory Fetch ──────────────────────────────────────────────────
async def memory_fetch(state: AgentState, memory_store, rag_engine) -> dict:
    facts  = await memory_store.get_facts(state.user_id, limit=15)
    chunks = await rag_engine.retrieve(state.user_input, state.user_id, top_k=5)
    return {
        "long_term_facts": [f.content for f in facts],
        "rag_chunks":      chunks
    }

# ── Approval Gate ─────────────────────────────────────────────────
async def approval_gate(state: AgentState) -> dict:
    all_tools = {t for task in state.subtasks for t in task.tools}
    risky     = all_tools & RISKY_TOOLS
    if risky and not state.approval_granted:
        return {
            "requires_approval": True,
            "approval_reason":   f"Approval needed for: {', '.join(risky)}"
        }
    return {"requires_approval": False, "approval_granted": True}

# ── Execution Engine ──────────────────────────────────────────────
async def execution_engine(state: AgentState, registry) -> dict:
    context = AgentContext(
        session_context = state.session_context,
        long_term_facts = state.long_term_facts,
        rag_chunks      = state.rag_chunks,
        user_id         = state.user_id,
        session_id      = state.session_id
    )
    results = {}
    for task in state.subtasks:
        if task.status != "pending":
            continue
        try:
            agent  = registry.get(task.agent)
            result = await agent.execute(task, context)
            task.status = "done" if result.success else "failed"
            results[task.id] = result.output if result.success else result.error
        except Exception as e:
            task.status  = "failed"
            results[task.id] = str(e)
    return {"agent_results": results, "subtasks": state.subtasks}

# ── Validator ─────────────────────────────────────────────────────
async def validator(state: AgentState, llm) -> dict:
    failed = [t for t in state.subtasks if t.status == "failed"]
    if failed and state.retry_count < state.max_retries:
        for t in failed:
            t.status = "pending"
        return {"retry_count": state.retry_count + 1,
                "validation_passed": False, "subtasks": state.subtasks}

    results_text = json.dumps(state.agent_results, indent=2)
    prompt = f"""User asked: {state.user_input}

Agent results:
{results_text}

Write a clear, helpful response to the user. Be concise."""

    response = await llm.ainvoke([
        SystemMessage(content="You are AURA, a helpful AI assistant."),
        HumanMessage(content=prompt)
    ])
    return {
        "final_response":    response.content,
        "validation_passed": True
    }

# ── Memory Write ──────────────────────────────────────────────────
async def memory_write(state: AgentState, memory_store) -> dict:
    await memory_store.save_turn(
        session_id = state.session_id,
        user_input = state.user_input,
        response   = state.final_response,
        intent     = state.intent
    )
    return {}

# ── Router functions ──────────────────────────────────────────────
def route_approval(state: AgentState) -> str:
    if state.requires_approval and not state.approval_granted:
        return "await_approval"
    return "execute"

def route_validation(state: AgentState) -> str:
    if not state.validation_passed and state.retry_count < state.max_retries:
        return "retry"
    return "complete"
```

### STEP 3.5 — packages/agents/master/graph.py
```python
from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from packages.agents.master.state import AgentState
from packages.agents.master.nodes import (
    intent_classifier, planner, memory_fetch,
    approval_gate, execution_engine, validator,
    memory_write, route_approval, route_validation
)
from packages.tools.llm import get_llm
from packages.tools.memory import MemoryStore
from packages.rag.engine import RAGEngine

def build_master_graph(registry, checkpointer=None):
    llm          = get_llm()
    memory_store = MemoryStore()
    rag          = RAGEngine()

    if checkpointer is None:
        checkpointer = MemorySaver()

    g = StateGraph(AgentState)

    g.add_node("intent_classifier",
               partial(intent_classifier, llm=llm))
    g.add_node("planner",
               partial(planner, registry=registry))
    g.add_node("memory_fetch",
               partial(memory_fetch, memory_store=memory_store, rag_engine=rag))
    g.add_node("approval_gate",  approval_gate)
    g.add_node("execution_engine",
               partial(execution_engine, registry=registry))
    g.add_node("validator",
               partial(validator, llm=llm))
    g.add_node("memory_write",
               partial(memory_write, memory_store=memory_store))

    g.set_entry_point("intent_classifier")
    g.add_edge("intent_classifier", "planner")
    g.add_edge("planner",           "memory_fetch")
    g.add_edge("memory_fetch",      "approval_gate")

    g.add_conditional_edges("approval_gate", route_approval, {
        "await_approval": END,
        "execute":        "execution_engine"
    })

    g.add_edge("execution_engine", "validator")

    g.add_conditional_edges("validator", route_validation, {
        "retry":    "execution_engine",
        "complete": "memory_write"
    })

    g.add_edge("memory_write", END)

    return g.compile(checkpointer=checkpointer)
```

### STEP 3.6 — packages/agents/registry.py
```python
from difflib import SequenceMatcher
from packages.agents.base.agent import BaseAgent
from packages.agents.base.manifest import AgentManifest

class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.manifest.name] = agent

    def get(self, name: str) -> BaseAgent:
        if name not in self._agents:
            return self._agents.get("PersonalAssistantAgent")
        return self._agents[name]

    def has(self, name: str) -> bool:
        return name in self._agents

    def best_match(self, description: str) -> str:
        best_name, best_score = "PersonalAssistantAgent", 0.0
        for name, agent in self._agents.items():
            score = agent.can_handle(description)
            if score > best_score:
                best_score, best_name = score, name
        return best_name

    def list_by_intent(self, intent: str) -> list[tuple[str, float]]:
        scores = [
            (name, agent.can_handle(intent))
            for name, agent in self._agents.items()
            if agent.manifest.enabled
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)

    async def health_check_all(self) -> dict[str, bool]:
        return {
            name: await agent.health_check()
            for name, agent in self._agents.items()
        }

async def bootstrap_registry(registry: AgentRegistry) -> None:
    from packages.agents.personal.agent import PersonalAssistantAgent
    from packages.agents.meeting.agent import MeetingAgent
    from packages.agents.coding.agent import CodingAgent
    from packages.agents.devops.agent import DevOpsAgent
    from packages.agents.communication.agent import CommunicationAgent
    from packages.agents.marketing.agent import MarketingAgent

    for AgentClass in [
        PersonalAssistantAgent,
        MeetingAgent,
        CodingAgent,
        DevOpsAgent,
        CommunicationAgent,
        MarketingAgent,
    ]:
        instance = AgentClass()
        registry.register(instance)
        print(f"  ✓ Registered {instance.manifest.name}")
```

### STEP 3.7 — packages/agents/personal/agent.py
```python
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import (
    AgentManifest, ToolManifest, PermissionLevel, CostTier
)
from packages.tools.llm import get_llm

class PersonalAssistantAgent(BaseAgent):
    manifest = AgentManifest(
        name        = "PersonalAssistantAgent",
        description = "General-purpose personal assistant for daily tasks, planning, and Q&A",
        intents     = ["personal", "general", "planning", "research", "question"],
        keywords    = ["help", "what", "how", "when", "why", "plan",
                       "remind", "schedule", "summarize", "explain"],
        tools = [
            ToolManifest(name="search_knowledge",
                         description="Search user knowledge base",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="web_search",
                         description="Search the web for current info",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.LOW),
        ],
        preferred_model = "auto",
        max_permission  = PermissionLevel.READ_ONLY,
        tags = ["general", "productivity"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm()
        system = self._build_system_prompt(context)
        try:
            response = await llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=task.description)
            ])
            return AgentResult(
                success    = True,
                output     = response.content,
                tool_calls = [{"tool": "llm_direct", "status": "ok"}]
            )
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))
```

### STEP 3.8 — packages/agents/meeting/agent.py
```python
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import (
    AgentManifest, ToolManifest, PermissionLevel, CostTier
)
from packages.tools.llm import get_llm
import json

class MeetingAgent(BaseAgent):
    manifest = AgentManifest(
        name        = "MeetingAgent",
        description = "Transcribes, analyses, and extracts knowledge from meetings",
        intents     = ["meeting", "transcription", "summary", "action_items"],
        keywords    = ["meeting", "call", "standup", "zoom", "teams",
                       "transcript", "record", "notes", "action"],
        tools = [
            ToolManifest(name="transcribe_audio",
                         description="Transcribe audio to text",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.FREE,
                         timeout_seconds=300),
            ToolManifest(name="extract_action_items",
                         description="Extract action items from transcript",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.LOW),
            ToolManifest(name="create_jira_tickets",
                         description="Create Jira tickets from action items",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="send_followup_email",
                         description="Send follow-up email",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.LOW),
        ],
        preferred_model = "local",
        max_permission  = PermissionLevel.APPROVAL_REQUIRED,
        tags = ["meeting", "productivity"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm(prefer_local=True)
        system = self._build_system_prompt(context)
        tool_calls = []
        try:
            transcript = task.metadata.get("transcript", task.description)
            prompt = f"""Analyse this meeting content and return JSON:
{{
  "summary": "3-5 sentence summary",
  "action_items": [{{"description":"...","owner":"...","due":"..."}}],
  "decisions": [{{"decision":"...","rationale":"..."}}],
  "risks": [{{"risk":"...","severity":"low|medium|high"}}],
  "key_topics": ["topic1","topic2"]
}}

Content: {transcript}"""
            response = await llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=prompt)
            ])
            tool_calls.append({"tool": "llm_analysis", "status": "ok"})
            try:
                raw = response.content
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                analysis = json.loads(raw.strip())
            except Exception:
                analysis = {"summary": response.content,
                            "action_items": [], "decisions": [],
                            "risks": [], "key_topics": []}
            return AgentResult(
                success    = True,
                output     = analysis,
                tool_calls = tool_calls
            )
        except Exception as e:
            return AgentResult(success=False, output=None,
                               tool_calls=tool_calls, error=str(e))
```

### STEP 3.9 — packages/agents/coding/agent.py
```python
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import (
    AgentManifest, ToolManifest, PermissionLevel, CostTier
)
from packages.tools.llm import get_llm

class CodingAgent(BaseAgent):
    manifest = AgentManifest(
        name        = "CodingAgent",
        description = "Software development: generate, review, refactor, document, test code",
        intents     = ["coding", "code_review", "refactor",
                       "unit_test", "documentation", "debug"],
        keywords    = ["code", "function", "class", "bug", "test",
                       "review", "refactor", "implement", "write", "fix",
                       "python", "javascript", "typescript", "sql"],
        tools = [
            ToolManifest(name="generate_code",
                         description="Generate code from requirements",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.MEDIUM),
            ToolManifest(name="review_code",
                         description="Review code for issues",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.MEDIUM),
            ToolManifest(name="generate_tests",
                         description="Generate unit tests",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.MEDIUM),
        ],
        preferred_model = "cloud",
        max_permission  = PermissionLevel.READ_ONLY,
        tags = ["development", "engineering"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm(prefer_local=False)
        system = self._build_system_prompt(context)
        system += "\nYou are an expert software engineer. Write clean, production-ready code with comments."
        try:
            response = await llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=task.description)
            ])
            return AgentResult(
                success    = True,
                output     = response.content,
                tool_calls = [{"tool": "llm_coding", "status": "ok"}]
            )
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))
```

### STEP 3.10 — packages/agents/devops/agent.py
```python
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import (
    AgentManifest, ToolManifest, PermissionLevel, CostTier
)
from packages.tools.llm import get_llm
from packages.tools.kubectl import kubectl_get, kubectl_describe

class DevOpsAgent(BaseAgent):
    manifest = AgentManifest(
        name        = "DevOpsAgent",
        description = "Kubernetes, Terraform, AWS/Azure, CI/CD, incident management",
        intents     = ["devops", "kubernetes", "infrastructure",
                       "incident", "deployment", "monitoring"],
        keywords    = ["kubectl", "pod", "deploy", "cluster", "terraform",
                       "aws", "azure", "ci", "cd", "jenkins", "pipeline",
                       "restart", "scale", "logs", "metrics"],
        tools = [
            ToolManifest(name="kubectl_get",
                         description="Read Kubernetes resources",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="kubectl_describe",
                         description="Describe Kubernetes resource",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="kubectl_delete",
                         description="Delete Kubernetes resource",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="kubectl_apply",
                         description="Apply Kubernetes manifest",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="terraform_plan",
                         description="Run terraform plan",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="terraform_apply",
                         description="Run terraform apply",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.FREE),
        ],
        preferred_model = "auto",
        max_permission  = PermissionLevel.APPROVAL_REQUIRED,
        tags = ["devops", "infrastructure"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm        = get_llm()
        system     = self._build_system_prompt(context)
        tool_calls = []
        cluster_info = ""

        # Gather cluster context if available
        try:
            pods = await kubectl_get("pods", "--all-namespaces")
            cluster_info = f"Current cluster state:\n{pods}"
            tool_calls.append({"tool": "kubectl_get", "status": "ok"})
        except Exception:
            cluster_info = "Cluster info unavailable (kubectl not configured)"
            tool_calls.append({"tool": "kubectl_get", "status": "skipped"})

        try:
            prompt = f"""{cluster_info}

Task: {task.description}

Provide:
1. Root cause analysis (if incident)
2. Recommended actions
3. Exact commands to run
4. Prevention measures"""
            response = await llm.ainvoke([
                SystemMessage(content=system + "\nYou are an expert DevOps/SRE engineer."),
                HumanMessage(content=prompt)
            ])
            tool_calls.append({"tool": "llm_analysis", "status": "ok"})
            return AgentResult(
                success    = True,
                output     = response.content,
                tool_calls = tool_calls
            )
        except Exception as e:
            return AgentResult(success=False, output=None,
                               tool_calls=tool_calls, error=str(e))
```

### STEP 3.11 — packages/agents/communication/agent.py
```python
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import (
    AgentManifest, ToolManifest, PermissionLevel, CostTier
)
from packages.tools.llm import get_llm

class CommunicationAgent(BaseAgent):
    manifest = AgentManifest(
        name        = "CommunicationAgent",
        description = "Draft, send, and summarise emails, Slack messages, Telegram, WhatsApp",
        intents     = ["communication", "email", "slack", "message",
                       "telegram", "whatsapp", "notification"],
        keywords    = ["email", "send", "message", "slack", "telegram",
                       "draft", "reply", "notify", "whatsapp", "dm"],
        tools = [
            ToolManifest(name="draft_email",
                         description="Draft an email",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.LOW),
            ToolManifest(name="send_email",
                         description="Send email via SMTP",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="post_slack",
                         description="Post message to Slack",
                         permission=PermissionLevel.APPROVAL_REQUIRED,
                         cost_tier=CostTier.FREE),
            ToolManifest(name="summarize_emails",
                         description="Summarize recent emails",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.LOW),
        ],
        preferred_model = "auto",
        max_permission  = PermissionLevel.APPROVAL_REQUIRED,
        tags = ["communication", "productivity"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm()
        system = self._build_system_prompt(context)
        system += "\nYou are an expert communication assistant. Draft clear, professional messages."
        try:
            response = await llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=task.description)
            ])
            return AgentResult(
                success    = True,
                output     = response.content,
                tool_calls = [{"tool": "draft_message", "status": "ok"}]
            )
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))
```

### STEP 3.12 — packages/agents/marketing/agent.py
```python
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import (
    AgentManifest, ToolManifest, PermissionLevel, CostTier
)
from packages.tools.llm import get_llm

class MarketingAgent(BaseAgent):
    manifest = AgentManifest(
        name        = "MarketingAgent",
        description = "Content creation, SEO, social media, campaign planning, analytics",
        intents     = ["marketing", "content", "seo", "social_media",
                       "blog", "campaign", "copywriting"],
        keywords    = ["blog", "post", "tweet", "linkedin", "instagram",
                       "seo", "keyword", "campaign", "content", "copy",
                       "social", "marketing", "ad", "brand"],
        tools = [
            ToolManifest(name="generate_blog_post",
                         description="Generate SEO-optimised blog post",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.MEDIUM),
            ToolManifest(name="generate_social_posts",
                         description="Generate platform-specific social posts",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.LOW),
            ToolManifest(name="seo_analyse",
                         description="Analyse SEO for content",
                         permission=PermissionLevel.READ_ONLY,
                         cost_tier=CostTier.LOW),
        ],
        preferred_model = "cloud",
        max_permission  = PermissionLevel.READ_ONLY,
        tags = ["marketing", "content"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm(prefer_local=False)
        system = self._build_system_prompt(context)
        system += "\nYou are a senior marketing specialist and copywriter. Create compelling, SEO-optimised content."
        try:
            response = await llm.ainvoke([
                SystemMessage(content=system),
                HumanMessage(content=task.description)
            ])
            return AgentResult(
                success    = True,
                output     = response.content,
                tool_calls = [{"tool": "generate_content", "status": "ok"}]
            )
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 4 — RAG PIPELINE
## Command to Claude Code: "Build Phase 4"
## ════════════════════════════════════════════════════════════════════

### STEP 4.1 — packages/tools/llm.py
```python
import os
from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama

def get_llm(prefer_local: bool = True, model: str = None):
    if prefer_local or not os.getenv("OPENAI_API_KEY"):
        local_model = model or os.getenv("DEFAULT_LOCAL_MODEL", "llama3.2:3b")
        try:
            return ChatOllama(
                model       = local_model,
                base_url    = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature = 0.7
            )
        except Exception:
            pass

    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model       = model or os.getenv("DEFAULT_CLOUD_MODEL", "claude-sonnet-4-6"),
            api_key     = os.getenv("ANTHROPIC_API_KEY"),
            temperature = 0.7,
            max_tokens  = 4096
        )

    return ChatOpenAI(
        model       = model or "gpt-4o-mini",
        api_key     = os.getenv("OPENAI_API_KEY"),
        temperature = 0.7
    )
```

### STEP 4.2 — packages/tools/memory.py
```python
import json
import redis.asyncio as redis
from datetime import datetime
from packages.db.connection import AsyncSessionFactory
from packages.db.models import MemoryFact, Message

class MemoryStore:
    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        if not self._redis:
            import os
            self._redis = redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                decode_responses=True
            )
        return self._redis

    async def get_facts(self, user_id: str, limit: int = 15) -> list:
        async with AsyncSessionFactory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(MemoryFact)
                .where(MemoryFact.user_id == user_id)
                .order_by(MemoryFact.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    async def save_turn(
        self,
        session_id: str,
        user_input: str,
        response:   str,
        intent:     str
    ) -> None:
        r = await self._get_redis()
        key  = f"session:{session_id}:history"
        turn = json.dumps({
            "user":     user_input,
            "assistant": response,
            "intent":   intent,
            "ts":       datetime.utcnow().isoformat()
        })
        await r.rpush(key, turn)
        await r.ltrim(key, -20, -1)   # keep last 20 turns
        await r.expire(key, 86400)    # 24h TTL

    async def get_session_context(self, session_id: str) -> list[dict]:
        r    = await self._get_redis()
        key  = f"session:{session_id}:history"
        raw  = await r.lrange(key, -10, -1)
        turns = []
        for item in raw:
            t = json.loads(item)
            turns.append({"role": "user",      "content": t["user"]})
            turns.append({"role": "assistant", "content": t["assistant"]})
        return turns
```

### STEP 4.3 — packages/tools/kubectl.py
```python
import asyncio
import shutil

async def kubectl_get(resource: str, namespace: str = "default") -> str:
    if not shutil.which("kubectl"):
        return "kubectl not available"
    proc = await asyncio.create_subprocess_exec(
        "kubectl", "get", resource, "-n", namespace, "-o", "wide",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode() if proc.returncode == 0 else stderr.decode()

async def kubectl_describe(resource: str, name: str,
                           namespace: str = "default") -> str:
    if not shutil.which("kubectl"):
        return "kubectl not available"
    proc = await asyncio.create_subprocess_exec(
        "kubectl", "describe", resource, name, "-n", namespace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode() if proc.returncode == 0 else stderr.decode()
```

### STEP 4.4 — packages/rag/engine.py (full)
```python
import hashlib, os
from .processor   import DocumentProcessor
from .chunker     import SemanticChunker
from .embedder    import EmbeddingPipeline
from .vector_store import VectorStore
from .retriever   import HybridRetriever
from packages.db.connection import AsyncSessionFactory
from packages.db.models     import Document, DocumentChunk

class RAGEngine:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.chunker   = SemanticChunker()
        self.embedder  = EmbeddingPipeline()
        self.store     = VectorStore(url=os.getenv("QDRANT_URL","http://qdrant:6333"))
        self.retriever = HybridRetriever(self.store, self.embedder)

    async def ingest(self, file_path: str, user_id: str) -> str:
        doc    = await self.processor.process(file_path)
        async with AsyncSessionFactory() as session:
            from sqlalchemy import select
            existing = await session.execute(
                select(Document)
                .where(Document.user_id == user_id)
                .where(Document.checksum == doc.checksum)
            )
            if existing.scalar_one_or_none():
                return doc.doc_id

        chunks = self.chunker.chunk(doc)
        chunks = await self.embedder.embed_chunks(chunks)
        await self.store.upsert_chunks(chunks)

        async with AsyncSessionFactory() as session:
            db_doc = Document(
                id          = doc.doc_id,
                user_id     = user_id,
                filename    = os.path.basename(file_path),
                source_path = file_path,
                doc_type    = doc.doc_type.value,
                checksum    = doc.checksum,
                chunk_count = len(chunks),
                size_bytes  = os.path.getsize(file_path)
            )
            session.add(db_doc)
            await session.commit()
        return doc.doc_id

    async def retrieve(self, query: str, user_id: str, top_k: int = 5) -> list[str]:
        chunks = await self.retriever.retrieve(query, filters={"user_id": user_id})
        return [
            f"[{c.get('filename','unknown')}]\n{c['content']}"
            for c in chunks[:top_k]
        ]
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 5 — DATABASE MODELS & MIGRATIONS
## Command to Claude Code: "Build Phase 5"
## ════════════════════════════════════════════════════════════════════

### STEP 5.1 — packages/db/connection.py
```python
import os
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://aura:aura_secret@localhost:5432/aura_db"
)

engine = create_async_engine(
    DATABASE_URL,
    pool_size     = 20,
    max_overflow  = 40,
    pool_pre_ping = True,
    pool_recycle  = 3600,
    echo          = False,
)

AsyncSessionFactory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    from packages.db.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_session():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def db_session():
    async with get_session() as s:
        yield s
```

### STEP 5.2 — migrations/001_initial_schema.sql
```sql
-- Full schema — run via: psql -U aura -d aura_db -f migrations/001_initial_schema.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    name          VARCHAR(255) NOT NULL,
    role          VARCHAR(50)  NOT NULL DEFAULT 'standard'
                  CHECK (role IN ('admin','power','standard','guest')),
    password_hash VARCHAR(255),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assistant_profiles (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL DEFAULT 'AURA',
    personality VARCHAR(50)  NOT NULL DEFAULT 'friendly',
    wake_phrase VARCHAR(100) NOT NULL DEFAULT 'Hey AURA',
    language    VARCHAR(10)  NOT NULL DEFAULT 'en',
    voice_id    VARCHAR(100),
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel    VARCHAR(50) NOT NULL DEFAULT 'web',
    title      VARCHAR(255),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at   TIMESTAMPTZ,
    metadata   JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id  UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        VARCHAR(20) NOT NULL,
    content     TEXT NOT NULL,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    model_used  VARCHAR(100),
    latency_ms  INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_messages_session
    ON messages(session_id, created_at DESC);

CREATE TABLE IF NOT EXISTS agent_runs (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id    UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name    VARCHAR(100) NOT NULL,
    intent        VARCHAR(100) NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'pending',
    input         JSONB NOT NULL DEFAULT '{}',
    output        JSONB,
    tokens_used   INTEGER NOT NULL DEFAULT 0,
    cost_usd      NUMERIC(10,6) NOT NULL DEFAULT 0,
    retry_count   SMALLINT NOT NULL DEFAULT 0,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at  TIMESTAMPTZ,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS tool_calls (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id      UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    tool_name   VARCHAR(100) NOT NULL,
    permission  VARCHAR(30) NOT NULL DEFAULT 'read_only',
    input       JSONB NOT NULL DEFAULT '{}',
    output      JSONB,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',
    duration_ms INTEGER,
    error       TEXT,
    called_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approvals (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id     UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    reason     TEXT NOT NULL,
    tools      JSONB NOT NULL DEFAULT '[]',
    status     VARCHAR(20) NOT NULL DEFAULT 'pending',
    decided_by UUID REFERENCES users(id),
    decided_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '10 minutes'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_approvals_pending
    ON approvals(status, expires_at) WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS documents (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename     VARCHAR(500) NOT NULL,
    source_path  TEXT NOT NULL,
    doc_type     VARCHAR(50) NOT NULL,
    checksum     VARCHAR(64) NOT NULL,
    chunk_count  INTEGER NOT NULL DEFAULT 0,
    size_bytes   BIGINT NOT NULL DEFAULT 0,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    refreshed_at TIMESTAMPTZ,
    metadata     JSONB NOT NULL DEFAULT '{}',
    UNIQUE(user_id, checksum)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id      UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    qdrant_id   BIGINT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(doc_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_chunks_fts
    ON document_chunks USING gin(to_tsvector('english', content));

CREATE TABLE IF NOT EXISTS memory_facts (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fact_type  VARCHAR(50) NOT NULL,
    subject    VARCHAR(255),
    content    TEXT NOT NULL,
    source     VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 1.0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_memory_facts_user
    ON memory_facts(user_id, fact_type);

CREATE TABLE IF NOT EXISTS meetings (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         VARCHAR(500),
    platform      VARCHAR(50),
    audio_path    TEXT,
    transcript    TEXT,
    duration_sec  INTEGER,
    summary       TEXT,
    decisions     JSONB NOT NULL DEFAULT '[]',
    risks         JSONB NOT NULL DEFAULT '[]',
    key_topics    JSONB NOT NULL DEFAULT '[]',
    held_at       TIMESTAMPTZ,
    processed_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meeting_action_items (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id  UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    owner       VARCHAR(255),
    due_date    DATE,
    priority    VARCHAR(20) DEFAULT 'medium',
    status      VARCHAR(20) DEFAULT 'open',
    jira_ticket VARCHAR(50),
    jira_url    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS llm_usage (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    run_id            UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
    provider          VARCHAR(50) NOT NULL,
    model             VARCHAR(100) NOT NULL,
    prompt_tokens     INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd          NUMERIC(10,6) NOT NULL DEFAULT 0,
    latency_ms        INTEGER,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_llm_usage_user
    ON llm_usage(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS integration_tokens (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform      VARCHAR(50) NOT NULL,
    access_token  TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry  TIMESTAMPTZ,
    scopes        JSONB NOT NULL DEFAULT '[]',
    workspace_id  VARCHAR(255),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(100) NOT NULL,
    resource_id UUID,
    ip_address  INET,
    details     JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_log_user
    ON audit_log(user_id, created_at DESC);
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 6 — FRONTEND (Next.js 14)
## Command to Claude Code: "Build Phase 6"
## ════════════════════════════════════════════════════════════════════

### STEP 6.1 — apps/frontend/package.json
```json
{
  "name": "aura-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev":   "next dev",
    "build": "next build",
    "start": "next start",
    "lint":  "next lint"
  },
  "dependencies": {
    "next":          "14.2.0",
    "react":         "18.3.0",
    "react-dom":     "18.3.0",
    "typescript":    "5.4.0",
    "@types/node":   "20.0.0",
    "@types/react":  "18.0.0",
    "tailwindcss":   "3.4.0",
    "autoprefixer":  "10.4.0",
    "postcss":       "8.4.0",
    "axios":         "1.7.0",
    "zustand":       "4.5.0",
    "lucide-react":  "0.383.0",
    "clsx":          "2.1.0",
    "tailwind-merge": "2.3.0"
  }
}
```

### STEP 6.2 — apps/frontend/src/app/layout.tsx
```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AURA AI-OS',
  description: 'Autonomous Unified Responsive Assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-100 min-h-screen`}>
        {children}
      </body>
    </html>
  )
}
```

### STEP 6.3 — apps/frontend/src/app/page.tsx
```tsx
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  useEffect(() => {
    const token = localStorage.getItem('aura_token')
    if (token) router.push('/chat')
    else router.push('/login')
  }, [])
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-purple-400 text-xl animate-pulse">
        Initialising AURA...
      </div>
    </div>
  )
}
```

### STEP 6.4 — apps/frontend/src/app/chat/page.tsx
```tsx
'use client'
import { useState, useEffect, useRef } from 'react'
import { Send, Mic, Upload, Settings, Zap } from 'lucide-react'

interface Message {
  id:      string
  role:    'user' | 'assistant' | 'status'
  content: string
  ts:      Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input,    setInput]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [status,   setStatus]   = useState('')
  const wsRef   = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const sessionId = useRef(`sess_${Date.now()}`)

  useEffect(() => {
    const wsUrl  = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    const token  = localStorage.getItem('aura_token') || ''
    const userId = localStorage.getItem('aura_user_id') || ''
    const ws = new WebSocket(
      `${wsUrl}/api/chat/ws/${sessionId.current}?token=${token}`
    )
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.type === 'token') {
        setMessages(prev => {
          const last = prev[prev.length - 1]
          if (last?.role === 'assistant') {
            return [...prev.slice(0, -1),
              {...last, content: last.content + data.content}]
          }
          return [...prev, {
            id: Date.now().toString(), role: 'assistant',
            content: data.content, ts: new Date()
          }]
        })
      } else if (data.type === 'status') {
        setStatus(`Processing: ${data.node}...`)
      } else if (data.type === 'done') {
        setLoading(false)
        setStatus('')
      } else if (data.type === 'approval_required') {
        setMessages(prev => [...prev, {
          id: Date.now().toString(), role: 'status',
          content: `⚠️ Approval needed: ${data.reason}`,
          ts: new Date()
        }])
        setLoading(false)
      }
    }
    wsRef.current = ws
    return () => ws.close()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return
    const userId = localStorage.getItem('aura_user_id') || ''
    const msg: Message = {
      id: Date.now().toString(), role: 'user',
      content: input, ts: new Date()
    }
    setMessages(prev => [...prev, msg])
    setLoading(true)
    wsRef.current.send(JSON.stringify({
      message: input, user_id: userId
    }))
    setInput('')
  }

  return (
    <div className="flex flex-col h-screen bg-gray-950">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
            <Zap size={16} className="text-white"/>
          </div>
          <div>
            <div className="font-semibold text-white">AURA</div>
            <div className="text-xs text-gray-500">
              {status || 'Ready'}
            </div>
          </div>
        </div>
        <Settings size={20} className="text-gray-500 cursor-pointer hover:text-white"/>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center mt-20">
            <div className="text-4xl mb-4">⚡</div>
            <div className="text-xl font-semibold text-white mb-2">
              Hello, I am AURA
            </div>
            <div className="text-gray-500 max-w-md mx-auto">
              Your AI operating system. Ask me anything, delegate tasks,
              analyse meetings, write code, or manage your infrastructure.
            </div>
          </div>
        )}
        {messages.map(msg => (
          <div key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-purple-600 text-white rounded-br-md'
                : msg.role === 'status'
                ? 'bg-amber-900/30 text-amber-300 border border-amber-800 text-xs'
                : 'bg-gray-800 text-gray-100 rounded-bl-md'
              }`}>
              <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"/>
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:0.1s]"/>
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:0.2s]"/>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef}/>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-end gap-3 bg-gray-900 rounded-2xl px-4 py-3">
          <textarea
            className="flex-1 bg-transparent text-white resize-none outline-none
                       text-sm leading-relaxed max-h-32 min-h-[24px]"
            placeholder="Ask AURA anything..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            rows={1}
          />
          <div className="flex items-center gap-2 pb-1">
            <button className="text-gray-500 hover:text-white transition-colors">
              <Upload size={18}/>
            </button>
            <button className="text-gray-500 hover:text-white transition-colors">
              <Mic size={18}/>
            </button>
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="w-8 h-8 bg-purple-600 hover:bg-purple-500 disabled:opacity-40
                         rounded-full flex items-center justify-center transition-colors">
              <Send size={14} className="text-white"/>
            </button>
          </div>
        </div>
        <div className="text-center text-xs text-gray-600 mt-2">
          AURA AI-OS v1.0 · Private & Self-Hosted
        </div>
      </div>
    </div>
  )
}
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 7 — VOICE SYSTEM
## Command to Claude Code: "Build Phase 7"
## ════════════════════════════════════════════════════════════════════

### STEP 7.1 — packages/voice/stt.py
```python
import asyncio, io, os, tempfile
from faster_whisper import WhisperModel

_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            "base",
            device          = "cpu",
            compute_type    = "int8",
            download_root   = "/tmp/whisper_models"
        )
    return _model

async def transcribe_audio(audio_bytes: bytes, language: str = "en") -> dict:
    model = get_whisper_model()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        segments, info = model.transcribe(
            tmp_path,
            language          = language,
            beam_size         = 5,
            vad_filter        = True,
            vad_parameters    = {"min_silence_duration_ms": 500}
        )
        transcript = " ".join(s.text for s in segments)
        return {
            "transcript": transcript.strip(),
            "language":   info.language,
            "duration":   info.duration
        }
    finally:
        os.unlink(tmp_path)

async def transcribe_file(file_path: str, language: str = "en") -> dict:
    model = get_whisper_model()
    segments, info = model.transcribe(
        file_path,
        language       = language,
        beam_size      = 5,
        vad_filter     = True
    )
    full_text = " ".join(s.text for s in segments)
    seg_list  = [
        {"start": s.start, "end": s.end, "text": s.text.strip()}
        for s in segments
    ]
    return {
        "transcript": full_text.strip(),
        "segments":   seg_list,
        "language":   info.language,
        "duration":   info.duration
    }
```

### STEP 7.2 — packages/voice/tts.py
```python
import asyncio, os, subprocess, tempfile

async def synthesize_speech(
    text:     str,
    voice_id: str = "en_US-lessac-medium"
) -> bytes:
    """
    Use Piper TTS for local speech synthesis.
    Install: pip install piper-tts
    Models: https://github.com/rhasspy/piper/releases
    """
    piper_path  = os.getenv("PIPER_PATH", "piper")
    models_dir  = os.getenv("PIPER_MODELS_DIR", "/tmp/piper_models")
    model_path  = f"{models_dir}/{voice_id}.onnx"

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            piper_path,
            "--model",  model_path,
            "--output_file", out_path,
            stdin  = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.PIPE
        )
        await proc.communicate(input=text.encode())

        if os.path.exists(out_path):
            with open(out_path, "rb") as f:
                return f.read()

        # Fallback: return silent WAV bytes
        return b""
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)
```

---

## ════════════════════════════════════════════════════════════════════
## PHASE 8 — INFRASTRUCTURE CONFIG
## Command to Claude Code: "Build Phase 8"
## ════════════════════════════════════════════════════════════════════

### STEP 8.1 — infrastructure/nginx/nginx.conf
```nginx
events { worker_connections 1024; }

http {
    upstream api      { server api:8000; }
    upstream frontend { server frontend:3000; }

    server {
        listen 80;
        server_name localhost;

        location /api/ {
            proxy_pass         http://api;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade $http_upgrade;
            proxy_set_header   Connection "upgrade";
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_read_timeout 300s;
        }

        location /metrics {
            proxy_pass http://api;
        }

        location / {
            proxy_pass       http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

### STEP 8.2 — infrastructure/monitoring/prometheus.yml
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'aura-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

---

## ════════════════════════════════════════════════════════════════════
## STARTUP SEQUENCE
## Command to Claude Code: "Run startup sequence"
## ════════════════════════════════════════════════════════════════════

### Run these commands in order after all files are created:
```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env and fill in your API keys

# 2. Build and start all services
make build
make up

# 3. Wait for services to be healthy (~60 seconds)
docker-compose ps

# 4. Run database migrations
make migrate

# 5. Pull Ollama models (takes time depending on connection)
make pull-models

# 6. Seed initial test user
make seed

# 7. Open in browser
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
# RabbitMQ: http://localhost:15672  (aura/aura_secret)
# MinIO:    http://localhost:9001   (aura_minio/aura_minio_secret)
```

---

## ════════════════════════════════════════════════════════════════════
## QUICK REFERENCE — CLAUDE CODE COMMANDS
## ════════════════════════════════════════════════════════════════════

| Say to Claude Code                    | What happens                              |
|---------------------------------------|-------------------------------------------|
| "Build Phase 1"                       | Creates docker-compose, .env, Makefile    |
| "Build Phase 2"                       | Creates FastAPI app, all routes           |
| "Build Phase 3"                       | Creates all 6 agents + registry + graph  |
| "Build Phase 4"                       | Creates RAG pipeline end-to-end           |
| "Build Phase 5"                       | Creates DB models + SQL migration         |
| "Build Phase 6"                       | Creates Next.js frontend + chat UI        |
| "Build Phase 7"                       | Creates voice STT/TTS pipeline            |
| "Build Phase 8"                       | Creates nginx + monitoring configs        |
| "Run startup sequence"                | Runs docker build + migrate + seed        |
| "Add a new agent called X"            | Scaffolds new agent following pattern     |
| "Add tool Y to DevOpsAgent"           | Extends agent with new tool               |
| "Fix the error in Phase N"            | Debugs and fixes issues                   |
| "Show me the API docs"                | Opens http://localhost:8000/docs          |
| "Run tests"                           | Executes pytest suite                     |

## IMPORTANT NOTES FOR CLAUDE CODE
1. Always run `cp .env.example .env` before first `docker-compose up`
2. The `packages/` directory must be on PYTHONPATH — set in Dockerfile
3. Ollama needs ~8GB disk for 7B models — ensure space before `make pull-models`
4. On Windows use `docker-compose` not `make` if GNU Make is not installed
5. If port conflicts occur: change ports in docker-compose.yml
6. Database URL uses asyncpg driver — do NOT use psycopg2 URLs

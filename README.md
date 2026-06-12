# AURA AI-OS

**Autonomous Unified Responsive Assistant** — A privacy-first, self-hosted AI Operating System.

## Quick Start

```bash
# 1. Clone / copy to D:\Project\Aura AI
# 2. Setup environment
cp .env.example .env
# Edit .env — add your API keys (ANTHROPIC_API_KEY or OPENAI_API_KEY)

# 3. Build & start
make build
make up

# 4. Initialize database
make migrate

# 5. Pull AI models (requires ~8GB disk)
make pull-models

# 6. Seed admin user
make seed
```

## Access

| Service  | URL                          | Credentials             |
|----------|------------------------------|-------------------------|
| Frontend | http://localhost:3000        | admin@aura.local / aura_admin_2024 |
| API Docs | http://localhost:8000/docs   | —                       |
| RabbitMQ | http://localhost:15672       | aura / aura_secret      |
| MinIO    | http://localhost:9001        | aura_minio / aura_minio_secret |

## Architecture

```
User → Next.js → WebSocket → FastAPI → LangGraph Master Agent
                                            ↓
                        ┌───────────────────┼───────────────────┐
                   PersonalAgent    MeetingAgent    CodingAgent
                   DevOpsAgent   CommAgent    MarketingAgent
                                            ↓
                              RAG (Qdrant + Ollama Embeddings)
                              Memory (Redis + PostgreSQL)
```

## Development

```bash
make logs        # tail all logs
make shell-api   # open API container shell
make test        # run tests
make fmt         # format code
```

## Claude Code Commands

Open this folder in VS Code with Claude Code and say:
- `"Build Phase 1"` — Infrastructure
- `"Build Phase 2"` — Backend API
- `"Build Phase 3"` — Agent System
- `"Build Phase 4"` — RAG Pipeline
- `"Add a new agent called X"` — Scaffold new agent

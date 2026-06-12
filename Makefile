.PHONY: help up down build rebuild migrate seed pull-models logs clean test fmt shell-api

help:
	@echo ""
	@echo "  AURA AI-OS — Makefile Commands"
	@echo "  ─────────────────────────────────────"
	@echo "  make up           Start all services (detached)"
	@echo "  make down         Stop all services"
	@echo "  make build        Build Docker images"
	@echo "  make rebuild      Force rebuild (no cache)"
	@echo "  make migrate      Run DB migrations (init_db)"
	@echo "  make seed         Seed admin user"
	@echo "  make pull-models  Pull Ollama LLM models"
	@echo "  make logs         Tail all service logs"
	@echo "  make clean        Remove all volumes (DESTRUCTIVE)"
	@echo "  make test         Run pytest suite"
	@echo "  make fmt          Format code (black + ruff)"
	@echo "  make shell-api    Open shell in api container"
	@echo ""

up:
	docker-compose up -d
	@echo ""
	@echo "  ✓ AURA AI-OS is running"
	@echo "  ─────────────────────────────────────"
	@echo "  Frontend : http://localhost:3000"
	@echo "  API      : http://localhost:8000"
	@echo "  API Docs : http://localhost:8000/docs"
	@echo "  RabbitMQ : http://localhost:15672  (aura / aura_secret)"
	@echo "  MinIO    : http://localhost:9001   (aura_minio / aura_minio_secret)"
	@echo "  Qdrant   : http://localhost:6333"
	@echo ""

down:
	docker-compose down

build:
	docker-compose build

rebuild:
	docker-compose build --no-cache

migrate:
	docker-compose exec api python -c "import asyncio; from packages.db.connection import init_db; asyncio.run(init_db())"

seed:
	docker-compose exec api python scripts/seed.py

pull-models:
	@echo "Pulling Ollama models (this may take several minutes)..."
	docker-compose exec ollama ollama pull llama3.2:3b
	docker-compose exec ollama ollama pull mistral:7b
	docker-compose exec ollama ollama pull nomic-embed-text
	docker-compose exec ollama ollama pull qwen2.5:7b
	@echo "✓ Models ready"

logs:
	docker-compose logs -f --tail=100

clean:
	@echo "WARNING: This will delete ALL data volumes."
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	docker-compose down -v
	@echo "✓ All volumes removed"

test:
	docker-compose exec api pytest packages/ apps/api/ -v --tb=short

fmt:
	docker-compose exec api black packages/ apps/api/ --line-length 100
	docker-compose exec api ruff check packages/ apps/api/ --fix

shell-api:
	docker-compose exec api bash

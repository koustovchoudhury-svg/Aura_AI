import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_BASE_URL:     str   = "http://ollama:11434"
    OPENAI_API_KEY:      str   = ""
    ANTHROPIC_API_KEY:   str   = ""
    DEFAULT_LOCAL_MODEL: str   = "llama3.2:3b"
    DEFAULT_CLOUD_MODEL: str   = "claude-sonnet-4-6"
    EMBED_MODEL:         str   = "nomic-embed-text"
    DATABASE_URL:        str   = "postgresql+asyncpg://aura:aura_secret@postgres:5432/aura_db"
    QDRANT_URL:          str   = "http://qdrant:6333"
    REDIS_URL:           str   = "redis://redis:6379/0"
    RABBITMQ_URL:        str   = "amqp://aura:aura_secret@rabbitmq:5672/"
    MINIO_ENDPOINT:      str   = "minio:9000"
    MINIO_ACCESS_KEY:    str   = "aura_minio"
    MINIO_SECRET_KEY:    str   = "aura_minio_secret"
    MINIO_BUCKET:        str   = "aura-files"
    JWT_SECRET:          str   = "change-me-in-production"
    JWT_ALGORITHM:       str   = "HS256"
    JWT_EXPIRE_MINUTES:  int   = 1440
    API_HOST:            str   = "0.0.0.0"
    API_PORT:            int   = 8000
    API_DEBUG:           bool  = True
    CORS_ORIGINS:        str   = "http://localhost:3000,http://localhost:8000"

    class Config:
        env_file = ".env"
        extra    = "ignore"

    @property
    def cors_origins_list(self) -> list:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()

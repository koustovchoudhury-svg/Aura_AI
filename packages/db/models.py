"""
SQLAlchemy async ORM models for AURA AI-OS.
All tables match migrations/001_initial_schema.sql exactly.
"""
import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger,
    Float, Text, Date, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, NUMERIC
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP

class Base(DeclarativeBase):
    pass

# ── Timestamp column helpers ──────────────────────────────────────────
def now_col():
    return Column(TIMESTAMP(timezone=True), server_default=func.now(),
                  nullable=False)

def now_update_col():
    return Column(TIMESTAMP(timezone=True), server_default=func.now(),
                  onupdate=func.now(), nullable=False)

# ── Users ─────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True,
                           default=uuid.uuid4)
    email         = Column(String(255), nullable=False, unique=True)
    name          = Column(String(255), nullable=False)
    role          = Column(String(50),  nullable=False, default="standard")
    password_hash = Column(String(255))
    is_active     = Column(Boolean, nullable=False, default=True)
    last_seen_at  = Column(TIMESTAMP(timezone=True))
    created_at    = now_col()
    updated_at    = now_update_col()

    profile      = relationship("AssistantProfile", back_populates="user",
                                 uselist=False, cascade="all, delete-orphan")
    sessions     = relationship("Session", back_populates="user",
                                 cascade="all, delete-orphan")
    documents    = relationship("Document", back_populates="user",
                                 cascade="all, delete-orphan")
    memory_facts = relationship("MemoryFact", back_populates="user",
                                 cascade="all, delete-orphan")
    meetings     = relationship("Meeting", back_populates="user",
                                 cascade="all, delete-orphan")

class AssistantProfile(Base):
    __tablename__ = "assistant_profiles"
    __table_args__ = (UniqueConstraint("user_id"),)

    id          = Column(UUID(as_uuid=True), primary_key=True,
                         default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True),
                         ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False)
    name        = Column(String(100), nullable=False, default="AURA")
    personality = Column(String(50),  nullable=False, default="friendly")
    wake_phrase = Column(String(100), nullable=False, default="Hey AURA")
    language    = Column(String(10),  nullable=False, default="en")
    voice_id    = Column(String(100))
    preferences = Column(JSONB, nullable=False, default=dict)
    created_at  = now_col()

    user = relationship("User", back_populates="profile")

# ── Sessions & Messages ───────────────────────────────────────────────
class Session(Base):
    __tablename__ = "sessions"

    id         = Column(UUID(as_uuid=True), primary_key=True,
                        default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True),
                        ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    channel    = Column(String(50), nullable=False, default="web")
    title      = Column(String(255))
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ended_at   = Column(TIMESTAMP(timezone=True))
    metadata_  = Column("metadata", JSONB, nullable=False, default=dict)

    user       = relationship("User", back_populates="sessions")
    messages   = relationship("Message", back_populates="session",
                               cascade="all, delete-orphan",
                               order_by="Message.created_at")
    agent_runs = relationship("AgentRun", back_populates="session",
                               cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("idx_messages_session_created", "session_id", "created_at"),
    )

    id          = Column(UUID(as_uuid=True), primary_key=True,
                         default=uuid.uuid4)
    session_id  = Column(UUID(as_uuid=True),
                         ForeignKey("sessions.id", ondelete="CASCADE"),
                         nullable=False)
    role        = Column(String(20),  nullable=False)
    content     = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=False, default=0)
    model_used  = Column(String(100))
    latency_ms  = Column(Integer)
    created_at  = now_col()

    session = relationship("Session", back_populates="messages")

# ── Agent Execution ───────────────────────────────────────────────────
class AgentRun(Base):
    __tablename__ = "agent_runs"

    id            = Column(UUID(as_uuid=True), primary_key=True,
                           default=uuid.uuid4)
    session_id    = Column(UUID(as_uuid=True),
                           ForeignKey("sessions.id", ondelete="CASCADE"),
                           nullable=False)
    agent_name    = Column(String(100), nullable=False)
    intent        = Column(String(100), nullable=False)
    status        = Column(String(20),  nullable=False, default="pending")
    input         = Column(JSONB, nullable=False, default=dict)
    output        = Column(JSONB)
    tokens_used   = Column(Integer, nullable=False, default=0)
    cost_usd      = Column(NUMERIC(10, 6), nullable=False, default=0)
    retry_count   = Column(Integer, nullable=False, default=0)
    started_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at  = Column(TIMESTAMP(timezone=True))
    error_message = Column(Text)

    session    = relationship("Session", back_populates="agent_runs")
    tool_calls = relationship("ToolCall", back_populates="run",
                               cascade="all, delete-orphan")
    approval   = relationship("Approval", back_populates="run",
                               uselist=False, cascade="all, delete-orphan")

class ToolCall(Base):
    __tablename__ = "tool_calls"

    id          = Column(UUID(as_uuid=True), primary_key=True,
                         default=uuid.uuid4)
    run_id      = Column(UUID(as_uuid=True),
                         ForeignKey("agent_runs.id", ondelete="CASCADE"),
                         nullable=False)
    tool_name   = Column(String(100), nullable=False)
    permission  = Column(String(30),  nullable=False, default="read_only")
    input       = Column(JSONB, nullable=False, default=dict)
    output      = Column(JSONB)
    status      = Column(String(20),  nullable=False, default="pending")
    duration_ms = Column(Integer)
    error       = Column(Text)
    called_at   = Column(TIMESTAMP(timezone=True), server_default=func.now())

    run = relationship("AgentRun", back_populates="tool_calls")

class Approval(Base):
    __tablename__ = "approvals"

    id         = Column(UUID(as_uuid=True), primary_key=True,
                        default=uuid.uuid4)
    run_id     = Column(UUID(as_uuid=True),
                        ForeignKey("agent_runs.id", ondelete="CASCADE"),
                        nullable=False)
    reason     = Column(Text, nullable=False)
    tools      = Column(JSONB, nullable=False, default=list)
    status     = Column(String(20), nullable=False, default="pending")
    decided_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    decided_at = Column(TIMESTAMP(timezone=True))
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = now_col()

    run = relationship("AgentRun", back_populates="approval")

# ── Knowledge ─────────────────────────────────────────────────────────
class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("user_id", "checksum"),)

    id           = Column(UUID(as_uuid=True), primary_key=True,
                          default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True),
                          ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    filename     = Column(String(500), nullable=False)
    source_path  = Column(Text, nullable=False)
    doc_type     = Column(String(50),  nullable=False)
    checksum     = Column(String(64),  nullable=False)
    chunk_count  = Column(Integer, nullable=False, default=0)
    size_bytes   = Column(BigInteger, nullable=False, default=0)
    ingested_at  = Column(TIMESTAMP(timezone=True), server_default=func.now())
    refreshed_at = Column(TIMESTAMP(timezone=True))
    metadata_    = Column("metadata", JSONB, nullable=False, default=dict)

    user   = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document",
                           cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("doc_id", "chunk_index"),)

    id          = Column(UUID(as_uuid=True), primary_key=True,
                         default=uuid.uuid4)
    doc_id      = Column(UUID(as_uuid=True),
                         ForeignKey("documents.id", ondelete="CASCADE"),
                         nullable=False)
    chunk_index = Column(Integer,    nullable=False)
    content     = Column(Text,       nullable=False)
    token_count = Column(Integer,    nullable=False, default=0)
    qdrant_id   = Column(BigInteger, nullable=False)
    created_at  = now_col()

    document = relationship("Document", back_populates="chunks")

class MemoryFact(Base):
    __tablename__ = "memory_facts"

    id         = Column(UUID(as_uuid=True), primary_key=True,
                        default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True),
                        ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    fact_type  = Column(String(50),  nullable=False)
    subject    = Column(String(255))
    content    = Column(Text, nullable=False)
    source     = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    expires_at = Column(TIMESTAMP(timezone=True))
    created_at = now_col()
    updated_at = now_update_col()

    user = relationship("User", back_populates="memory_facts")

# ── Meetings ──────────────────────────────────────────────────────────
class Meeting(Base):
    __tablename__ = "meetings"

    id           = Column(UUID(as_uuid=True), primary_key=True,
                          default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True),
                          ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    title        = Column(String(500))
    platform     = Column(String(50))
    audio_path   = Column(Text)
    transcript   = Column(Text)
    duration_sec = Column(Integer)
    summary      = Column(Text)
    decisions    = Column(JSONB, nullable=False, default=list)
    risks        = Column(JSONB, nullable=False, default=list)
    key_topics   = Column(JSONB, nullable=False, default=list)
    held_at      = Column(TIMESTAMP(timezone=True))
    processed_at = Column(TIMESTAMP(timezone=True))
    created_at   = now_col()

    user         = relationship("User", back_populates="meetings")
    action_items = relationship("MeetingActionItem", back_populates="meeting",
                                 cascade="all, delete-orphan")

class MeetingActionItem(Base):
    __tablename__ = "meeting_action_items"

    id          = Column(UUID(as_uuid=True), primary_key=True,
                         default=uuid.uuid4)
    meeting_id  = Column(UUID(as_uuid=True),
                         ForeignKey("meetings.id", ondelete="CASCADE"),
                         nullable=False)
    description = Column(Text, nullable=False)
    owner       = Column(String(255))
    due_date    = Column(Date)
    priority    = Column(String(20), default="medium")
    status      = Column(String(20), default="open")
    jira_ticket = Column(String(50))
    jira_url    = Column(Text)
    created_at  = now_col()

    meeting = relationship("Meeting", back_populates="action_items")

# ── Usage & Integrations ──────────────────────────────────────────────
class LlmUsage(Base):
    __tablename__ = "llm_usage"
    __table_args__ = (
        Index("idx_llm_usage_user_created", "user_id", "created_at"),
    )

    id                = Column(UUID(as_uuid=True), primary_key=True,
                               default=uuid.uuid4)
    user_id           = Column(UUID(as_uuid=True),
                               ForeignKey("users.id", ondelete="CASCADE"),
                               nullable=False)
    run_id            = Column(UUID(as_uuid=True),
                               ForeignKey("agent_runs.id", ondelete="SET NULL"))
    provider          = Column(String(50),  nullable=False)
    model             = Column(String(100), nullable=False)
    prompt_tokens     = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    cost_usd          = Column(NUMERIC(10, 6), nullable=False, default=0)
    latency_ms        = Column(Integer)
    created_at        = now_col()

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id           = Column(UUID(as_uuid=True), primary_key=True,
                          default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True),
                          ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    name         = Column(String(255), nullable=False)
    cron_expr    = Column(String(100), nullable=False)
    instruction  = Column(Text, nullable=False)
    enabled      = Column(Boolean, nullable=False, default=True)
    last_run_at  = Column(TIMESTAMP(timezone=True))
    last_result  = Column(Text)
    created_at   = now_col()
    updated_at   = now_update_col()

class IntegrationToken(Base):
    __tablename__ = "integration_tokens"
    __table_args__ = (UniqueConstraint("user_id", "platform"),)

    id            = Column(UUID(as_uuid=True), primary_key=True,
                           default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True),
                           ForeignKey("users.id", ondelete="CASCADE"),
                           nullable=False)
    platform      = Column(String(50),  nullable=False)
    access_token  = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_expiry  = Column(TIMESTAMP(timezone=True))
    scopes        = Column(JSONB, nullable=False, default=list)
    workspace_id  = Column(String(255))
    created_at    = now_col()
    updated_at    = now_update_col()

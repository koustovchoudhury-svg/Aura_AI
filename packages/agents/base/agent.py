from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from .manifest import AgentManifest, ToolManifest

@dataclass
class AgentContext:
    session_context:  list = field(default_factory=list)
    long_term_facts:  list = field(default_factory=list)
    rag_chunks:       list = field(default_factory=list)
    user_id:          str  = ""
    session_id:       str  = ""

@dataclass
class AgentResult:
    success:     bool
    output:      Any
    tool_calls:  list = field(default_factory=list)
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
        matches = sum(1 for k in self.manifest.keywords if k.lower() in intent.lower())
        return min(matches / max(len(self.manifest.keywords), 1), 0.9)

    async def health_check(self) -> bool:
        return self.manifest.enabled

    def get_tools(self) -> list:
        return self.manifest.tools

    def _build_system_prompt(self, context: AgentContext) -> str:
        facts   = "\n".join(str(f.content) if hasattr(f,'content') else str(f) for f in context.long_term_facts)
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

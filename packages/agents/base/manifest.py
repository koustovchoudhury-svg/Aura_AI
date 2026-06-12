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

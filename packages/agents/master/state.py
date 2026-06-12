from typing import Annotated, Any, Literal
from pydantic import BaseModel
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
    user_input:          str
    user_id:             str  = ""
    session_id:          str  = ""
    intent:              str  = ""
    intent_confidence:   float = 0.0
    subtasks:            list[TaskItem] = []
    session_context:     list[dict] = []
    long_term_facts:     list[str]  = []
    rag_chunks:          list[str]  = []
    requires_approval:   bool = False
    approval_granted:    bool = False
    approval_reason:     str  = ""
    approval_responded:  bool = False
    retry_count:         int  = 0
    max_retries:         int  = 3
    agent_results:       dict = {}
    final_response:      str  = ""
    validation_passed:   bool = False
    messages:            Annotated[list, add_messages] = []

from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from packages.agents.master.state import AgentState
from packages.agents.master.nodes import (
    intent_classifier, planner, memory_fetch, approval_gate,
    execution_engine, validator, memory_write,
    route_approval, route_validation
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
    g.add_node("intent_classifier",  partial(intent_classifier, llm=llm))
    g.add_node("planner",            partial(planner, registry=registry))
    g.add_node("memory_fetch",       partial(memory_fetch, memory_store=memory_store, rag_engine=rag))
    g.add_node("approval_gate",      approval_gate)
    g.add_node("execution_engine",   partial(execution_engine, registry=registry))
    g.add_node("validator",          partial(validator, llm=llm))
    g.add_node("memory_write",       partial(memory_write, memory_store=memory_store))

    g.set_entry_point("intent_classifier")
    g.add_edge("intent_classifier", "planner")
    g.add_edge("planner",           "memory_fetch")
    g.add_edge("memory_fetch",      "approval_gate")
    g.add_conditional_edges("approval_gate", route_approval,
                            {"await_approval": END, "execute": "execution_engine"})
    g.add_edge("execution_engine",  "validator")
    g.add_conditional_edges("validator", route_validation,
                            {"retry":"execution_engine","complete":"memory_write"})
    g.add_edge("memory_write", END)

    return g.compile(checkpointer=checkpointer)

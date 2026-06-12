import asyncio, json
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.master.state import AgentState, TaskItem
from packages.agents.base.agent import AgentContext

RISKY_TOOLS = {
    "kubectl_delete","kubectl_apply","terraform_apply","execute_shell","host_action",
    "send_email","post_slack","post_telegram",
    "create_jira","aws_terminate","github_merge"
}

async def intent_classifier(state: AgentState, llm) -> dict:
    prompt = f"""Classify this request. Return ONLY valid JSON, no markdown.

Request: {state.user_input}

If the user asks to run a system/shell command, check status, or perform file/folder operations
INSIDE THE AURA SANDBOX (paths under /app, /host/Documents, etc.),
set "agent":"DevOpsAgent", "tools":["execute_shell"], and "metadata":{{"command":"<the exact shell command>"}}.
Use standard Linux commands: ls, find, cat, mkdir, cp, mv, rm, grep, curl, etc.

If the user asks to open/launch an application on THEIR COMPUTER (e.g. "open Notepad", "launch Chrome"),
open a URL/website in their default browser, or read/write/list files/folders ON THEIR COMPUTER
(e.g. "what's in my Downloads folder", "open my resume.docx"),
set "agent":"DevOpsAgent", "tools":["host_action"], and "metadata":{{"action":"open_app|open_url|list_dir|read_file|write_file","target":"<app name, url, or absolute Windows path>","content":"<only for write_file>"}}.

Return:
{{"intent":"personal|meeting|coding|devops|communication|marketing","confidence":0.9,"subtasks":[{{"id":"t1","description":"task description","agent":"PersonalAssistantAgent","tools":[],"depends_on":[],"metadata":{{}}}}]}}"""
    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are a task classifier. Return only valid JSON."),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip().strip("```json").strip("```").strip()
        parsed = json.loads(raw)
        return {
            "intent":            parsed.get("intent","personal"),
            "intent_confidence": parsed.get("confidence",0.8),
            "subtasks": [TaskItem(**t) for t in parsed.get("subtasks",[])]
        }
    except Exception:
        return {"intent":"personal","intent_confidence":0.5,
                "subtasks":[TaskItem(id="t1",description=state.user_input,
                                     agent="PersonalAssistantAgent",tools=[])]}

async def planner(state: AgentState, registry) -> dict:
    tasks = state.subtasks
    for task in tasks:
        if not registry.has(task.agent):
            task.agent = registry.best_match(task.description)
    return {"subtasks": tasks}

async def memory_fetch(state: AgentState, memory_store, rag_engine) -> dict:
    try:
        facts  = await memory_store.get_facts(state.user_id, limit=15)
        chunks = await rag_engine.retrieve(state.user_input, state.user_id, top_k=5)
        return {
            "long_term_facts": [getattr(f,"content",str(f)) for f in facts],
            "rag_chunks":      chunks
        }
    except Exception:
        return {"long_term_facts":[],"rag_chunks":[]}

async def approval_gate(state: AgentState) -> dict:
    all_tools = {t for task in state.subtasks for t in task.tools}
    risky     = all_tools & RISKY_TOOLS
    if risky and not state.approval_granted:
        return {"requires_approval":True,
                "approval_reason":f"Approval needed for: {', '.join(risky)}"}
    return {"requires_approval":False,"approval_granted":True}

async def _get_disabled_tools(user_id: str) -> set:
    try:
        from sqlalchemy import select
        from packages.db.connection import AsyncSessionFactory
        from packages.db.models import AssistantProfile
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(AssistantProfile).where(AssistantProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            if profile and profile.preferences:
                return set(profile.preferences.get("disabled_tools", []))
    except Exception:
        pass
    return set()

async def execution_engine(state: AgentState, registry) -> dict:
    context = AgentContext(
        session_context=state.session_context,
        long_term_facts=state.long_term_facts,
        rag_chunks=state.rag_chunks,
        user_id=state.user_id,
        session_id=state.session_id
    )
    disabled = await _get_disabled_tools(state.user_id)
    results = {}
    for task in state.subtasks:
        if task.status != "pending":
            continue
        blocked = [t for t in task.tools if t in disabled]
        if blocked:
            task.status = "failed"
            results[task.id] = f"Tool(s) disabled by user in Skills settings: {', '.join(blocked)}"
            continue
        try:
            agent  = registry.get(task.agent)
            result = await agent.execute(task, context)
            task.status      = "done" if result.success else "failed"
            results[task.id] = result.output if result.success else result.error
        except Exception as e:
            task.status = "failed"
            results[task.id] = str(e)
    return {"agent_results":results,"subtasks":state.subtasks}

async def validator(state: AgentState, llm) -> dict:
    failed = [t for t in state.subtasks if t.status == "failed"]
    if failed and state.retry_count < state.max_retries:
        for t in failed: t.status = "pending"
        return {"retry_count":state.retry_count+1,"validation_passed":False,"subtasks":state.subtasks}
    results_text = json.dumps(state.agent_results, indent=2, default=str)
    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are AURA, a helpful AI assistant. Be concise and clear."),
            HumanMessage(content=f"User asked: {state.user_input}\n\nResults:\n{results_text}\n\nWrite a clear response.")
        ])
        return {"final_response":response.content,"validation_passed":True}
    except Exception as e:
        return {"final_response":str(state.agent_results),"validation_passed":True}

async def memory_write(state: AgentState, memory_store) -> dict:
    try:
        await memory_store.save_turn(
            session_id=state.session_id, user_input=state.user_input,
            response=state.final_response, intent=state.intent
        )
    except Exception:
        pass
    return {"validation_passed": state.validation_passed}

def route_approval(state: AgentState) -> str:
    if state.requires_approval and not state.approval_granted:
        return "await_approval"
    return "execute"

def route_validation(state: AgentState) -> str:
    if not state.validation_passed and state.retry_count < state.max_retries:
        return "retry"
    return "complete"

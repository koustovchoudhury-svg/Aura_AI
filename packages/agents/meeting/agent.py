import json
from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import AgentManifest, ToolManifest, PermissionLevel, CostTier
from packages.tools.llm import get_llm

class MeetingAgent(BaseAgent):
    manifest = AgentManifest(
        name="MeetingAgent",
        description="Transcribes, analyses, and extracts knowledge from meetings",
        intents=["meeting","transcription","summary","action_items","meeting_notes"],
        keywords=["meeting","call","standup","zoom","teams","transcript","record","notes","action","minutes"],
        tools=[
            ToolManifest(name="transcribe_audio",description="Transcribe audio",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.FREE,timeout_seconds=300),
            ToolManifest(name="extract_action_items",description="Extract action items",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.LOW),
            ToolManifest(name="create_jira_tickets",description="Create Jira tickets",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE),
        ],
        preferred_model="local", max_permission=PermissionLevel.APPROVAL_REQUIRED,
        tags=["meeting","productivity"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm(prefer_local=True)
        system = self._build_system_prompt(context)
        try:
            transcript = task.metadata.get("transcript", task.description)
            prompt = f"""Analyse this meeting content. Return ONLY valid JSON:
{{"summary":"3-5 sentence summary","action_items":[{{"description":"...","owner":"...","due":"..."}}],"decisions":[{{"decision":"...","rationale":"..."}}],"risks":[{{"risk":"...","severity":"low|medium|high"}}],"key_topics":["topic1"]}}

Content: {transcript[:3000]}"""
            response = await llm.ainvoke([SystemMessage(content=system),
                                          HumanMessage(content=prompt)])
            try:
                raw = response.content.strip().strip("```json").strip("```").strip()
                analysis = json.loads(raw)
            except Exception:
                analysis = {"summary":response.content,"action_items":[],"decisions":[],"risks":[],"key_topics":[]}
            return AgentResult(success=True, output=analysis,
                               tool_calls=[{"tool":"llm_analysis","status":"ok"}])
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))

from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import AgentManifest, ToolManifest, PermissionLevel, CostTier
from packages.tools.llm import get_llm

class PersonalAssistantAgent(BaseAgent):
    manifest = AgentManifest(
        name="PersonalAssistantAgent",
        description="General-purpose personal assistant for daily tasks, planning, Q&A",
        intents=["personal","general","planning","research","question","help"],
        keywords=["help","what","how","when","why","plan","remind","schedule","summarize","explain","tell","find"],
        tools=[
            ToolManifest(name="search_knowledge",description="Search knowledge base",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.FREE),
        ],
        preferred_model="auto", max_permission=PermissionLevel.READ_ONLY,
        tags=["general","productivity"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm()
        system = self._build_system_prompt(context)
        try:
            response = await llm.ainvoke([SystemMessage(content=system),
                                          HumanMessage(content=task.description)])
            return AgentResult(success=True, output=response.content,
                               tool_calls=[{"tool":"llm_direct","status":"ok"}])
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))

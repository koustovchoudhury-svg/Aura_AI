from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import AgentManifest, ToolManifest, PermissionLevel, CostTier
from packages.tools.llm import get_llm

class CodingAgent(BaseAgent):
    manifest = AgentManifest(
        name="CodingAgent",
        description="Software development: generate, review, refactor, document, test code",
        intents=["coding","code_review","refactor","unit_test","documentation","debug","implement"],
        keywords=["code","function","class","bug","test","review","refactor","implement","write","fix","python","javascript","typescript","sql","api"],
        tools=[
            ToolManifest(name="generate_code",description="Generate code",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.MEDIUM),
            ToolManifest(name="review_code",description="Review code",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.MEDIUM),
        ],
        preferred_model="cloud", max_permission=PermissionLevel.READ_ONLY,
        tags=["development","engineering"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm(prefer_local=False)
        system = self._build_system_prompt(context)
        system += "\nYou are an expert software engineer. Write clean, production-ready, well-commented code."
        try:
            response = await llm.ainvoke([SystemMessage(content=system),
                                          HumanMessage(content=task.description)])
            return AgentResult(success=True, output=response.content,
                               tool_calls=[{"tool":"llm_coding","status":"ok"}])
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))

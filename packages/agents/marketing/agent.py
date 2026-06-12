from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import AgentManifest, ToolManifest, PermissionLevel, CostTier
from packages.tools.llm import get_llm

class MarketingAgent(BaseAgent):
    manifest = AgentManifest(
        name="MarketingAgent",
        description="Content creation, SEO, social media, campaign planning, analytics",
        intents=["marketing","content","seo","social_media","blog","campaign","copywriting"],
        keywords=["blog","post","tweet","linkedin","instagram","seo","keyword","campaign","content","copy","social","marketing","ad","brand","write"],
        tools=[
            ToolManifest(name="generate_blog",description="Write SEO blog post",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.MEDIUM),
            ToolManifest(name="generate_social",description="Write social posts",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.LOW),
        ],
        preferred_model="cloud", max_permission=PermissionLevel.READ_ONLY,
        tags=["marketing","content"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm(prefer_local=False)
        system = self._build_system_prompt(context)
        system += "\nYou are a senior marketing specialist and copywriter. Create compelling, SEO-optimised content."
        try:
            response = await llm.ainvoke([SystemMessage(content=system),
                                          HumanMessage(content=task.description)])
            return AgentResult(success=True, output=response.content,
                               tool_calls=[{"tool":"generate_content","status":"ok"}])
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))

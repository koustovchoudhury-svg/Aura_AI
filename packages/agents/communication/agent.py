from langchain_core.messages import SystemMessage, HumanMessage
from packages.agents.base.agent import BaseAgent, AgentContext, AgentResult
from packages.agents.base.manifest import AgentManifest, ToolManifest, PermissionLevel, CostTier
from packages.tools.llm import get_llm

class CommunicationAgent(BaseAgent):
    manifest = AgentManifest(
        name="CommunicationAgent",
        description="Draft, send, summarise emails, Slack, Telegram, WhatsApp messages",
        intents=["communication","email","slack","message","telegram","whatsapp","notification"],
        keywords=["email","send","message","slack","telegram","draft","reply","notify","whatsapp","dm","communicate"],
        tools=[
            ToolManifest(name="draft_email",description="Draft email",
                         permission=PermissionLevel.READ_ONLY,cost_tier=CostTier.LOW),
            ToolManifest(name="send_email",description="Send email",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE),
            ToolManifest(name="post_slack",description="Post to Slack",
                         permission=PermissionLevel.APPROVAL_REQUIRED,cost_tier=CostTier.FREE),
        ],
        preferred_model="auto", max_permission=PermissionLevel.APPROVAL_REQUIRED,
        tags=["communication","productivity"]
    )

    async def execute(self, task, context: AgentContext) -> AgentResult:
        llm    = get_llm()
        system = self._build_system_prompt(context)
        system += "\nYou are an expert communication assistant. Draft clear, professional, concise messages."
        try:
            response = await llm.ainvoke([SystemMessage(content=system),
                                          HumanMessage(content=task.description)])
            return AgentResult(success=True, output=response.content,
                               tool_calls=[{"tool":"draft_message","status":"ok"}])
        except Exception as e:
            return AgentResult(success=False, output=None, error=str(e))

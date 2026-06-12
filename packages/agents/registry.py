from packages.agents.base.agent import BaseAgent
from packages.agents.base.manifest import AgentManifest

class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.manifest.name] = agent

    def get(self, name: str) -> BaseAgent:
        return self._agents.get(name, self._agents.get("PersonalAssistantAgent"))

    def has(self, name: str) -> bool:
        return name in self._agents

    def list_all(self) -> list:
        return [a.manifest for a in self._agents.values() if a.manifest.enabled]

    def best_match(self, description: str) -> str:
        best_name, best_score = "PersonalAssistantAgent", 0.0
        for name, agent in self._agents.items():
            score = agent.can_handle(description)
            if score > best_score:
                best_score, best_name = score, name
        return best_name

    async def health_check_all(self) -> dict:
        return {name: await agent.health_check() for name, agent in self._agents.items()}

async def bootstrap_registry(registry: "AgentRegistry") -> None:
    from packages.agents.personal.agent      import PersonalAssistantAgent
    from packages.agents.meeting.agent       import MeetingAgent
    from packages.agents.coding.agent        import CodingAgent
    from packages.agents.devops.agent        import DevOpsAgent
    from packages.agents.communication.agent import CommunicationAgent
    from packages.agents.marketing.agent     import MarketingAgent

    for AgentClass in [PersonalAssistantAgent, MeetingAgent, CodingAgent,
                       DevOpsAgent, CommunicationAgent, MarketingAgent]:
        instance = AgentClass()
        registry.register(instance)
        print(f"  ✓ {instance.manifest.name}")

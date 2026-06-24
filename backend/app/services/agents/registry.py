from app.services.agents.architect_agent import ArchitectAgent
from app.services.agents.base import BaseAgent
from app.services.agents.developer_agent import DeveloperAgent
from app.services.agents.planner_agent import PlannerAgent
from app.services.agents.qa_agent import QAAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        self._agents[name] = agent

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())


def create_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register_agent("planner", PlannerAgent())
    registry.register_agent("architect", ArchitectAgent())
    registry.register_agent("developer", DeveloperAgent())
    registry.register_agent("qa", QAAgent())
    return registry

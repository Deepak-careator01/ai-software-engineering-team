from app.services.agents.registry import AgentRegistry, create_default_registry
from app.services.core.exceptions import ServiceError


class AgentNotFoundError(ServiceError):
    """Raised when the requested agent is not registered."""


class AgentService:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._registry = registry or create_default_registry()

    def run(self, agent_name: str, input: dict) -> dict:
        agent = self._registry.get_agent(agent_name)
        if agent is None:
            raise AgentNotFoundError(f"Agent '{agent_name}' not found")
        return agent.run(input)

    def list_agents(self) -> list[str]:
        return self._registry.list_agents()

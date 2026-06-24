from app.services.agents.base import BaseAgent


class ArchitectAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "architect"

    def run(self, input: dict) -> dict:
        return {
            "agent": "architect",
            "architecture": [
                "system design overview",
                "api layer design",
                "data flow structure",
            ],
            "status": "success",
        }

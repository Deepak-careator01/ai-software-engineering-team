from app.services.agents.base import BaseAgent


class QAAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "qa"

    def run(self, input: dict) -> dict:
        return {
            "agent": "qa",
            "tests": [
                "unit tests for services",
                "api endpoint validation",
                "integration checks",
            ],
            "status": "success",
        }

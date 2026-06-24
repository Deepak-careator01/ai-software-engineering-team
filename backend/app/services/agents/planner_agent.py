from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator
from app.services.llm.utils import LLMResponseParser

_FALLBACK_RESPONSE: dict[str, Any] = {
    "agent": "planner",
    "analysis": "Fallback analysis due to LLM failure",
    "steps": [
        "analyze requirement",
        "break into tasks",
        "define architecture",
    ],
    "tasks": [
        "identify requirements",
        "design system",
        "plan execution",
    ],
    "status": "success",
}


class PlannerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "planner"

    def run(self, input: dict) -> dict:
        goal = input.get("goal", "build a software system")

        try:
            service = LLMService()
            result = service.generate_structured_json(
                f"""You are a Senior Software Architect Planner.

Goal: {goal}

Return a structured JSON object with:
1. analysis: short explanation of requirement
2. steps: list of 3-5 high-level development steps
3. tasks: list of actionable tasks"""
            )

            parsed = result.get("parsed")
            if not isinstance(parsed, dict):
                return SchemaValidator.validate_planner(dict(_FALLBACK_RESPONSE))

            analysis = parsed.get("analysis")
            steps = LLMResponseParser.normalize_string_list(parsed.get("steps", []))
            tasks = LLMResponseParser.normalize_string_list(parsed.get("tasks", []))

            if not isinstance(analysis, str) or not steps or not tasks:
                return SchemaValidator.validate_planner(dict(_FALLBACK_RESPONSE))

            return SchemaValidator.validate_planner(
                {
                    "agent": "planner",
                    "analysis": analysis,
                    "steps": steps,
                    "tasks": tasks,
                    "status": "success",
                }
            )
        except Exception:
            return SchemaValidator.validate_planner(dict(_FALLBACK_RESPONSE))

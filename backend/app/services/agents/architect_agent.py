from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator
from app.services.llm.utils import LLMResponseParser

_FALLBACK_ARCHITECTURE = [
    "frontend layer",
    "backend API layer",
    "database layer",
]


class ArchitectAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "architect"

    def run(self, input: dict) -> dict:
        goal = input.get("goal", "build a software system")

        try:
            service = LLMService()
            result = service.generate_structured_json(
                f"""You are a senior software architect.

Given the user goal, generate a structured system architecture.

Return ONLY valid JSON in this format:

{{
  "architecture": [
    "component 1",
    "component 2",
    "component 3"
  ]
}}

User goal:
{goal}"""
            )

            parsed = result.get("parsed")
            if not isinstance(parsed, dict):
                return self._fallback_response()

            architecture = parsed.get("architecture")
            if not isinstance(architecture, list) or not architecture:
                return self._fallback_response()

            return SchemaValidator.validate_architect(
                {
                    "agent": "architect",
                    "architecture": LLMResponseParser.normalize_string_list(
                        architecture
                    ),
                    "status": "success",
                }
            )
        except Exception:
            return self._fallback_response()

    def _fallback_response(self) -> dict[str, Any]:
        return SchemaValidator.validate_architect(
            {
                "agent": "architect",
                "architecture": list(_FALLBACK_ARCHITECTURE),
                "status": "success",
            }
        )

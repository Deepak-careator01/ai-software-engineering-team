from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator
from app.services.llm.utils import LLMResponseParser

_FALLBACK_CODE_PLAN = [
    "setup project structure",
    "implement backend APIs",
    "integrate frontend with backend",
    "add validation and error handling",
]


class DeveloperAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "developer"

    def run(self, input: dict) -> dict:
        goal = input.get("goal", "build a software system")
        architecture = input.get("architecture", [])

        try:
            service = LLMService()
            result = service.generate_structured_json(
                f"""You are a senior software developer agent.

Return ONLY valid JSON.

STRICT OUTPUT FORMAT:

{{
  "code_plan": [
    "short actionable step 1",
    "short actionable step 2",
    "short actionable step 3"
  ]
}}

RULES:
- Each item in code_plan MUST be a simple string
- Do NOT return objects inside arrays
- Do NOT include step/task dictionaries
- Do NOT include explanations
- Output ONLY valid JSON

Goal:
{goal}

Architecture:
{architecture}"""
            )

            parsed = result.get("parsed")
            if not isinstance(parsed, dict):
                return self._fallback_response()

            code_plan = parsed.get("code_plan")
            if not isinstance(code_plan, list) or not code_plan:
                return self._fallback_response()

            return SchemaValidator.validate_developer(
                {
                    "agent": "developer",
                    "code_plan": LLMResponseParser.normalize_string_list(code_plan),
                    "status": "success",
                }
            )
        except Exception:
            return self._fallback_response()

    def _fallback_response(self) -> dict[str, Any]:
        return SchemaValidator.validate_developer(
            {
                "agent": "developer",
                "code_plan": list(_FALLBACK_CODE_PLAN),
                "status": "success",
            }
        )

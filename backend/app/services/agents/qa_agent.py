from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator
from app.services.llm.utils import LLMResponseParser

_FALLBACK_TESTS = [
    "validate API endpoints",
    "check input validation",
    "verify architecture consistency",
    "test error handling",
    "check integration flow",
]


class QAAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "qa"

    def run(self, input: dict) -> dict:
        goal = input.get("goal", "build a software system")
        architecture = input.get("architecture", [])
        code_plan = input.get("code_plan", [])

        try:
            service = LLMService()
            result = service.generate_structured_json(
                f"""You are a QA testing agent.

Return ONLY valid JSON.

STRICT OUTPUT FORMAT:

{{
  "tests": [
    "test case 1 description",
    "test case 2 description",
    "test case 3 description"
  ]
}}

RULES:
- Each test MUST be a simple string
- Do NOT return nested objects
- Do NOT include steps, metadata, or explanations
- Output ONLY valid JSON

Goal:
{goal}

Architecture:
{architecture}

Code Plan:
{code_plan}"""
            )

            parsed = result.get("parsed")
            if not isinstance(parsed, dict):
                return self._fallback_response()

            tests = parsed.get("tests")
            if not isinstance(tests, list) or not tests:
                return self._fallback_response()

            return SchemaValidator.validate_qa(
                {
                    "agent": "qa",
                    "tests": LLMResponseParser.normalize_string_list(tests),
                    "status": "success",
                }
            )
        except Exception:
            return self._fallback_response()

    def _fallback_response(self) -> dict[str, Any]:
        return SchemaValidator.validate_qa(
            {
                "agent": "qa",
                "tests": list(_FALLBACK_TESTS),
                "status": "success",
            }
        )

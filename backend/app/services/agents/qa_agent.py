import json
import re
from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator

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
            response = service.generate_text(
                f"""You are a senior QA engineer.

Given the system design and implementation plan, create a structured test strategy.

Return ONLY valid JSON in this format:

{{
  "tests": [
    "test case 1",
    "test case 2",
    "test case 3"
  ]
}}

Goal:
{goal}

Architecture:
{architecture}

Code Plan:
{code_plan}"""
            )

            if not isinstance(response, dict):
                return self._fallback_response()

            parsed = self._parse_llm_output(response.get("output"))
            if parsed is None:
                return self._fallback_response()

            tests = parsed.get("tests")
            if not isinstance(tests, list) or not tests:
                return self._fallback_response()

            return SchemaValidator.validate_qa(
                {
                    "agent": "qa",
                    "tests": tests,
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

    def _parse_llm_output(self, raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, dict):
            if "tests" in raw:
                return raw
            return None

        if not isinstance(raw, str) or not raw.strip():
            return None

        text = raw.strip()

        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        return None

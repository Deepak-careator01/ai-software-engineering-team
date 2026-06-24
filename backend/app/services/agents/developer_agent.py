import json
import re
from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator

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
            response = service.generate_text(
                f"""You are a senior software engineer.

Given the system architecture and goal, create a detailed implementation plan.

Return ONLY valid JSON in this format:

{{
  "code_plan": [
    "step 1",
    "step 2",
    "step 3"
  ]
}}

Goal:
{goal}

Architecture:
{architecture}"""
            )

            if not isinstance(response, dict):
                return self._fallback_response()

            parsed = self._parse_llm_output(response.get("output"))
            if parsed is None:
                return self._fallback_response()

            code_plan = parsed.get("code_plan")
            if not isinstance(code_plan, list) or not code_plan:
                return self._fallback_response()

            return SchemaValidator.validate_developer(
                {
                    "agent": "developer",
                    "code_plan": code_plan,
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

    def _parse_llm_output(self, raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, dict):
            if "code_plan" in raw:
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

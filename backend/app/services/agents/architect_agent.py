import json
import re
from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator

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
            response = service.generate_text(
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

            if not isinstance(response, dict):
                return self._fallback_response()

            parsed = self._parse_llm_output(response.get("output"))
            if parsed is None:
                return self._fallback_response()

            architecture = parsed.get("architecture")
            if not isinstance(architecture, list) or not architecture:
                return self._fallback_response()

            return SchemaValidator.validate_architect(
                {
                    "agent": "architect",
                    "architecture": architecture,
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

    def _parse_llm_output(self, raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, dict):
            if "architecture" in raw:
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

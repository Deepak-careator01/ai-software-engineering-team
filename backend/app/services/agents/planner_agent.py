import json
import re
from typing import Any

from app.services.agents.base import BaseAgent
from app.services.core.llm_service import LLMService
from app.services.core.schema_validator import SchemaValidator

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
            result = service.generate_text(
                f"""
You are a Senior Software Architect Planner.

Goal: {goal}

Return a structured JSON with:
1. analysis: short explanation of requirement
2. steps: list of 3-5 high-level development steps
3. tasks: list of actionable tasks

Return ONLY valid JSON.
"""
            )

            if not isinstance(result, dict):
                return SchemaValidator.validate_planner(dict(_FALLBACK_RESPONSE))

            output = result.get("output")
            parsed = self._parse_llm_output(output)
            if parsed is None:
                return SchemaValidator.validate_planner(dict(_FALLBACK_RESPONSE))

            analysis = parsed.get("analysis")
            steps = parsed.get("steps")
            tasks = parsed.get("tasks")

            if (
                not isinstance(analysis, str)
                or not isinstance(steps, list)
                or not isinstance(tasks, list)
                or not steps
                or not tasks
            ):
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

    def _parse_llm_output(self, raw: Any) -> dict[str, Any] | None:
        if isinstance(raw, dict):
            if "analysis" in raw and "steps" in raw and "tasks" in raw:
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

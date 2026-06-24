from typing import Any

from app.services.llm.router import LLMRouter
from app.services.llm.utils import (
    JSON_RETRY_RULES,
    JSON_STRICT_RULES,
    LLMResponseParser,
)


class LLMService:
    def __init__(self) -> None:
        self._router = LLMRouter()

    def generate_text(self, prompt: str) -> dict[str, Any]:
        result = self._router.generate_text(prompt)
        return {
            "provider_used": result.get("provider_used"),
            "output": result.get("output"),
            "parsed": None,
        }

    def generate_json(self, prompt: str) -> dict[str, Any]:
        result = self._router.generate_json(prompt)
        return {
            "provider_used": result.get("provider_used"),
            "output": result.get("output"),
            "parsed": None,
        }

    def generate_structured_json(self, prompt: str) -> dict[str, Any]:
        full_prompt = f"{prompt.strip()}\n\n{JSON_STRICT_RULES}"
        result = self.generate_text(full_prompt)
        try:
            parsed = LLMResponseParser.parse_output(result.get("output"))
        except ValueError:
            retry_prompt = f"{JSON_RETRY_RULES}\n\n{full_prompt}"
            result = self.generate_text(retry_prompt)
            parsed = LLMResponseParser.parse_output(result.get("output"))
        return {
            "provider_used": result.get("provider_used"),
            "output": result.get("output"),
            "parsed": parsed,
        }

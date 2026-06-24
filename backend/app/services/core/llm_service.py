from typing import Any

from app.services.llm.router import LLMRouter


class LLMService:
    def __init__(self) -> None:
        self._router = LLMRouter()

    def generate_text(self, prompt: str) -> dict[str, Any]:
        return self._router.generate_text(prompt)

    def generate_json(self, prompt: str) -> dict[str, Any]:
        return self._router.generate_json(prompt)

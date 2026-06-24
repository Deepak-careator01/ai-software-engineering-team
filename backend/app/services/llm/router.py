import app.core.config  # noqa: F401 — load .env before provider init

from typing import Any

from app.services.llm.base import BaseLLM
from app.services.llm.gemini import GeminiLLM
from app.services.llm.groq import GroqLLM
from app.services.llm.ollama import OllamaLLM


class LLMRouter:
    def __init__(self) -> None:
        self._providers: list[tuple[str, BaseLLM]] = [
            ("gemini", GeminiLLM()),
            ("groq", GroqLLM()),
            ("ollama", OllamaLLM()),
        ]

    def generate_text(self, prompt: str) -> dict[str, Any]:
        return self._run_with_fallback(prompt, "generate_text")

    def generate_json(self, prompt: str) -> dict[str, Any]:
        return self._run_with_fallback(prompt, "generate_json")

    def _run_with_fallback(
        self, prompt: str, method: str
    ) -> dict[str, Any]:
        for provider_name, provider in self._providers:
            try:
                output = getattr(provider, method)(prompt)
                return {
                    "provider_used": provider_name,
                    "output": output,
                }
            except Exception:
                continue

        return {
            "provider_used": "none",
            "output": "All providers failed",
        }


if __name__ == "__main__":
    from app.services.llm.router import LLMRouter

    router = LLMRouter()
    print(router.generate_text("Write JSON for a todo app architecture"))

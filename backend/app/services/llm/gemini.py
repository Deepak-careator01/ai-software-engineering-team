import os

from app.services.llm.base import BaseLLM


class GeminiLLM(BaseLLM):
    def __init__(self) -> None:
        self._api_key = os.environ.get("GEMINI_API_KEY")

    def generate_text(self, prompt: str) -> str:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        return "[gemini-mock] " + prompt

    def generate_json(self, prompt: str) -> dict:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        return {
            "provider": "gemini",
            "response": prompt,
        }

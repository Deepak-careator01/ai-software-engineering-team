import os

from app.services.llm.base import BaseLLM


class GroqLLM(BaseLLM):
    def __init__(self) -> None:
        self._api_key = os.environ.get("GROQ_API_KEY")

    def generate_text(self, prompt: str) -> str:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not set")
        return "[groq-mock] " + prompt

    def generate_json(self, prompt: str) -> dict:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is not set")
        return {
            "provider": "groq",
            "response": prompt,
        }

import json
import os
import re

import httpx

from app.services.llm.base import BaseLLM

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL = "llama-3.1-8b-instant"


class GroqLLM(BaseLLM):
    def __init__(self) -> None:
        self._api_key = os.getenv("GROQ_API_KEY")

    def generate_text(self, prompt: str) -> str:
        if not self._api_key:
            raise ValueError("GROQ_API_KEY missing")

        try:
            response = httpx.post(
                _GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": _GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            text = (content or "").strip()
            if not text:
                raise ValueError("Empty Groq response")
            return text
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Groq API call failed: {exc}") from exc

    def generate_json(self, prompt: str) -> dict:
        return _parse_json_text(self.generate_text(prompt))


def _parse_json_text(text: str) -> dict:
    stripped = text.strip()

    try:
        data = json.loads(stripped)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    raise ValueError("Groq response is not valid JSON")

import json
import os
import re

import google.generativeai as genai

from app.services.llm.base import BaseLLM

_GEMINI_MODEL = "gemini-2.0-flash"


class GeminiLLM(BaseLLM):
    def __init__(self) -> None:
        self._api_key = os.getenv("GEMINI_API_KEY")

    def generate_text(self, prompt: str) -> str:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY missing")

        try:
            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(_GEMINI_MODEL)
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            if not text:
                raise ValueError("Empty Gemini response")
            return text
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

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

    raise ValueError("Gemini response is not valid JSON")

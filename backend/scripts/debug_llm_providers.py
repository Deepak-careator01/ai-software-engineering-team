"""Temporary LLM provider debug script. Safe to delete after verification."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.llm.router import LLMRouter


def _mask(value: str | None) -> str:
    if not value:
        return "NOT SET"
    return f"SET (len={len(value)}, prefix={value[:4]}...)"


def test_router(prompt: str = "test prompt") -> None:
    print("=== LLM Provider Debug ===")
    print(f"GEMINI_API_KEY: {_mask(os.environ.get('GEMINI_API_KEY'))}")
    print(f"GROQ_API_KEY:   {_mask(os.environ.get('GROQ_API_KEY'))}")
    print()

    router = LLMRouter()

    text_result = router.generate_text(prompt)
    print("generate_text result:")
    print(f"  provider_used: {text_result.get('provider_used')}")
    output = text_result.get("output")
    preview = str(output)[:120] + ("..." if len(str(output)) > 120 else "")
    print(f"  output preview: {preview}")
    print(f"  is_mock_gemini: {str(output).startswith('[gemini-mock]')}")
    print(f"  is_mock_groq:   {str(output).startswith('[groq-mock]')}")
    print(f"  is_mock_ollama: {str(output).startswith('[ollama-mock]')}")
    print()

    json_result = router.generate_json(prompt)
    print("generate_json result:")
    print(f"  provider_used: {json_result.get('provider_used')}")
    print(f"  output: {json_result.get('output')}")


if __name__ == "__main__":
    test_router()

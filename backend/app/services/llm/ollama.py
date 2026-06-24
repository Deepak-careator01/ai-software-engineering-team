from app.services.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    def generate_text(self, prompt: str) -> str:
        return "[ollama-mock] " + prompt

    def generate_json(self, prompt: str) -> dict:
        return {
            "provider": "ollama",
            "response": prompt,
        }

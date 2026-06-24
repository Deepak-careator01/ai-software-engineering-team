import json
import re
from typing import Any

JSON_STRICT_RULES = """
Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

Output must be a valid JSON object or array only.
"""

JSON_RETRY_RULES = """
Fix the previous response.
Return ONLY valid JSON.
No explanation.
"""


class LLMResponseParser:
    @staticmethod
    def extract_json(text: str) -> dict[str, Any]:
        """
        Extract JSON from LLM response safely.
        Handles:
        - raw JSON
        - markdown blocks
        - mixed text + JSON
        """
        if not text:
            raise ValueError("Empty LLM response")

        stripped = text.strip()

        try:
            data = json.loads(stripped)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        markdown_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL | re.IGNORECASE
        )
        if markdown_match:
            try:
                data = json.loads(markdown_match.group(1))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        raise ValueError("No valid JSON found in LLM response")

    @staticmethod
    def parse_output(raw: Any) -> dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            return LLMResponseParser.extract_json(raw)
        raise ValueError("Invalid LLM output type")

    @staticmethod
    def normalize_string_list(items: Any) -> list[str]:
        if items is None:
            return []
        if not isinstance(items, list):
            items = [items]

        normalized: list[str] = []
        for item in items:
            if isinstance(item, str):
                stripped = item.strip()
                if stripped.startswith("{"):
                    try:
                        parsed_item = json.loads(stripped)
                        if isinstance(parsed_item, dict):
                            normalized.extend(
                                LLMResponseParser.normalize_string_list([parsed_item])
                            )
                            continue
                    except json.JSONDecodeError:
                        pass
                normalized.append(stripped)
            elif isinstance(item, dict):
                value = (
                    item.get("step")
                    or item.get("description")
                    or item.get("name")
                    or item.get("title")
                    or item.get("test")
                )
                if value:
                    normalized.append(str(value).strip())
                else:
                    tasks = item.get("tasks")
                    if isinstance(tasks, list) and tasks:
                        for task in tasks:
                            normalized.append(str(task).strip())
                    else:
                        normalized.append(json.dumps(item))
            else:
                normalized.append(str(item))
        return normalized

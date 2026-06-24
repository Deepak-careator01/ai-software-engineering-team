from typing import Any


class SchemaValidator:
    @staticmethod
    def validate_planner(output: dict) -> dict:
        normalized = dict(output) if isinstance(output, dict) else {}

        normalized["agent"] = SchemaValidator._as_string(
            normalized.get("agent"), "planner"
        )
        normalized["analysis"] = SchemaValidator._as_string(
            normalized.get("analysis"), ""
        )
        normalized["steps"] = SchemaValidator._as_string_list(normalized.get("steps"))
        normalized["tasks"] = SchemaValidator._as_string_list(normalized.get("tasks"))
        normalized["status"] = SchemaValidator._as_string(
            normalized.get("status"), "success"
        )

        return normalized

    @staticmethod
    def validate_architect(output: dict) -> dict:
        normalized = dict(output) if isinstance(output, dict) else {}

        normalized["agent"] = SchemaValidator._as_string(
            normalized.get("agent"), "architect"
        )
        normalized["architecture"] = SchemaValidator._as_string_list(
            normalized.get("architecture")
        )
        normalized["status"] = SchemaValidator._as_string(
            normalized.get("status"), "success"
        )

        return normalized

    @staticmethod
    def validate_developer(output: dict) -> dict:
        normalized = dict(output) if isinstance(output, dict) else {}

        normalized["agent"] = SchemaValidator._as_string(
            normalized.get("agent"), "developer"
        )
        normalized["code_plan"] = SchemaValidator._as_string_list(
            normalized.get("code_plan")
        )
        normalized["status"] = SchemaValidator._as_string(
            normalized.get("status"), "success"
        )

        return normalized

    @staticmethod
    def validate_qa(output: dict) -> dict:
        normalized = dict(output) if isinstance(output, dict) else {}

        normalized["agent"] = SchemaValidator._as_string(normalized.get("agent"), "qa")
        normalized["tests"] = SchemaValidator._as_string_list(normalized.get("tests"))
        normalized["status"] = SchemaValidator._as_string(
            normalized.get("status"), "success"
        )

        return normalized

    @staticmethod
    def _as_string(value: Any, default: str = "") -> str:
        if value is None:
            return default
        return str(value)

    @staticmethod
    def _as_string_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

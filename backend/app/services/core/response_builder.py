from typing import Any


class ResponseBuilder:
    @staticmethod
    def success(data: Any, message: str | None = None) -> dict[str, Any]:
        return {
            "success": True,
            "message": message,
            "data": data,
        }

    @staticmethod
    def error(message: str, code: str | None = None) -> dict[str, Any]:
        response: dict[str, Any] = {
            "success": False,
            "message": message,
            "data": None,
        }
        if code is not None:
            response["code"] = code
        return response

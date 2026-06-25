from typing import Any

from pydantic import BaseModel


class WorkflowRunRequest(BaseModel):
    goal: str


class WorkflowRunResponse(BaseModel):
    result: dict[str, Any]
    status: str = "success"
    workflow_id: str | None = None

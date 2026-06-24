from fastapi import APIRouter
from pydantic import BaseModel

from app.models.workflow import WorkflowRunRequest, WorkflowRunResponse
from app.services.agents.graphs.software_engineering_graph import app_graph

router = APIRouter(prefix="/workflow", tags=["workflow"])


class ModuleHealthResponse(BaseModel):
    status: str
    module: str


@router.get("/health", response_model=ModuleHealthResponse)
async def module_health() -> ModuleHealthResponse:
    return ModuleHealthResponse(status="ok", module="workflow")


@router.post("/run", response_model=WorkflowRunResponse)
def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    result = app_graph.invoke({"goal": request.goal})

    return WorkflowRunResponse(
        result=result,
        status="success",
    )

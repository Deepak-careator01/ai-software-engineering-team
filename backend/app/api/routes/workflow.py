from fastapi import APIRouter
from pydantic import BaseModel

from app.models.workflow import WorkflowRunRequest, WorkflowRunResponse
from app.services.agents.graphs.software_engineering_graph import app_graph
from app.services.db.workflow_repository import WorkflowRepository

router = APIRouter(prefix="/workflow", tags=["workflow"])
_workflow_repository = WorkflowRepository()


class ModuleHealthResponse(BaseModel):
    status: str
    module: str


@router.get("/health", response_model=ModuleHealthResponse)
async def module_health() -> ModuleHealthResponse:
    return ModuleHealthResponse(status="ok", module="workflow")


@router.post("/run", response_model=WorkflowRunResponse)
def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    result = app_graph.invoke({"goal": request.goal})
    workflow_id = _workflow_repository.persist_workflow_run(
        goal=request.goal,
        graph_state=result,
    )

    return WorkflowRunResponse(
        result=result,
        status="success",
        workflow_id=workflow_id,
    )

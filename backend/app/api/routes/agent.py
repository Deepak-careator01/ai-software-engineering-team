from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.agent import AgentListResponse, AgentRunRequest, AgentRunResponse
from app.services.agents import AgentNotFoundError, AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


class ModuleHealthResponse(BaseModel):
    status: str
    module: str


@router.get("/health", response_model=ModuleHealthResponse)
async def module_health() -> ModuleHealthResponse:
    return ModuleHealthResponse(status="ok", module="agent")


@router.get("/list", response_model=AgentListResponse)
async def list_agents() -> AgentListResponse:
    return AgentListResponse(agents=AgentService().list_agents())


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    try:
        output = AgentService().run(request.agent_name, request.input)
    except AgentNotFoundError:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentRunResponse(
        agent=output.get("agent", request.agent_name),
        output=output,
    )

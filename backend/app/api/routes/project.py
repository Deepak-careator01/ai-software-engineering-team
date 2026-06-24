from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/project", tags=["project"])


class ModuleHealthResponse(BaseModel):
    status: str
    module: str


@router.get("/health", response_model=ModuleHealthResponse)
async def module_health() -> ModuleHealthResponse:
    return ModuleHealthResponse(status="ok", module="project")

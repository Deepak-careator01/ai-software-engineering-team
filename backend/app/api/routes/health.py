from fastapi import APIRouter

from app.core.config import API_VERSION, SERVICE_NAME
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=API_VERSION,
    )

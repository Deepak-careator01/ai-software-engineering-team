from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent, health, project, workflow
from app.core.config import API_VERSION, SERVICE_NAME


def create_app() -> FastAPI:
    app = FastAPI(
        title=SERVICE_NAME,
        version=API_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(agent.router, prefix="/api/v1")
    app.include_router(project.router, prefix="/api/v1")
    app.include_router(workflow.router, prefix="/api/v1")

    return app


app = create_app()

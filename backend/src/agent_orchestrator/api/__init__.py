"""FastAPI application and route definitions."""

from __future__ import annotations

from fastapi import FastAPI

from agent_orchestrator.api.routes.agents import router as agents_router
from agent_orchestrator.api.routes.conversations import router as conversations_router
from agent_orchestrator.api.routes.events import router as events_router
from agent_orchestrator.api.routes.health import router as health_router
from agent_orchestrator.api.routes.orchestration import router as orchestration_router


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    application = FastAPI(
        title="Agent Orchestrator",
        version="0.1.0",
    )
    application.include_router(health_router)
    application.include_router(conversations_router)
    application.include_router(events_router)
    application.include_router(agents_router)
    application.include_router(orchestration_router)
    return application


app = create_app()

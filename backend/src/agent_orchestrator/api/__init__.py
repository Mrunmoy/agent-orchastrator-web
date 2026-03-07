"""FastAPI application and route definitions."""

from __future__ import annotations

from fastapi import FastAPI

from agent_orchestrator.api.routes.health import router as health_router


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    application = FastAPI(
        title="Agent Orchestrator",
        version="0.1.0",
    )
    application.include_router(health_router)
    return application


app = create_app()

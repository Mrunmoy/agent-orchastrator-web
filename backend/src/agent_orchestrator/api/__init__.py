"""FastAPI application and route definitions."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_orchestrator.api.routes.agents import router as agents_router
from agent_orchestrator.api.routes.conversations import router as conversations_router
from agent_orchestrator.api.routes.events import router as events_router
from agent_orchestrator.api.routes.health import router as health_router
from agent_orchestrator.api.routes.orchestration import router as orchestration_router


def _allowed_origins_from_env() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS")
    if raw is None or not raw.strip():
        # Safe default for local dev; override explicitly for LAN/prod.
        return ["http://127.0.0.1:5173", "http://localhost:5173"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    application = FastAPI(
        title="Agent Orchestrator",
        version="0.1.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins_from_env(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(conversations_router)
    application.include_router(events_router)
    application.include_router(agents_router)
    application.include_router(orchestration_router)
    return application


app = create_app()

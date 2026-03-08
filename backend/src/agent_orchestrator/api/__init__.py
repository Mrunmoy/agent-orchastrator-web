"""FastAPI application and route definitions."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_orchestrator.api.routes.agents import router as agents_router
from agent_orchestrator.api.routes.artifacts import router as artifacts_router
from agent_orchestrator.api.routes.conversation_agents import (
    router as conversation_agents_router,
)
from agent_orchestrator.api.routes.conversations import router as conversations_router
from agent_orchestrator.api.routes.events import router as events_router
from agent_orchestrator.api.routes.health import router as health_router
from agent_orchestrator.api.routes.orchestration import router as orchestration_router
from agent_orchestrator.api.routes.tasks import router as tasks_router

logger = logging.getLogger(__name__)


def _allowed_origins_from_env() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS")
    if raw is not None and raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    env = os.getenv("ENV", "").lower()
    dev_mode = os.getenv("DEV_MODE", "").lower() in {"1", "true", "yes"}
    if env in {"dev", "development"} or dev_mode:
        return ["*"]
    return [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: start/stop the BatchExecutor."""
    from agent_orchestrator.api.db_provider import get_db
    from agent_orchestrator.runtime.executor import BatchExecutor

    executor = BatchExecutor(get_db())
    await executor.start()
    logger.info("BatchExecutor started in lifespan")
    yield
    await executor.stop()
    logger.info("BatchExecutor stopped in lifespan")


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    application = FastAPI(
        title="Agent Orchestrator",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins_from_env(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router, prefix="/api")
    application.include_router(conversations_router, prefix="/api")
    application.include_router(events_router, prefix="/api")
    application.include_router(agents_router, prefix="/api")
    application.include_router(conversation_agents_router, prefix="/api")
    application.include_router(orchestration_router, prefix="/api")
    application.include_router(tasks_router, prefix="/api")
    application.include_router(artifacts_router, prefix="/api")
    return application


app = create_app()

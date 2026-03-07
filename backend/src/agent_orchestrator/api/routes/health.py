"""Health and state endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from agent_orchestrator.api.responses import ok_response

router = APIRouter()


@router.get("/health")
def health() -> dict[str, Any]:
    """Liveness / readiness probe."""
    return ok_response({"status": "healthy"})


@router.get("/state")
def state() -> dict[str, Any]:
    """Return app version and current status."""
    return ok_response({"version": "0.1.0", "status": "idle"})

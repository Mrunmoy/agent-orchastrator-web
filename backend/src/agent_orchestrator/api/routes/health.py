"""Health and state endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter()


def ok_response(data: dict[str, Any]) -> dict[str, Any]:
    """Wrap data in the standard ok envelope."""
    return {"ok": True, "data": data}


@router.get("/health")
def health() -> dict[str, Any]:
    """Liveness / readiness probe."""
    return ok_response({"status": "healthy"})


@router.get("/state")
def state() -> dict[str, Any]:
    """Return app version and current status."""
    return ok_response({"version": "0.1.0", "status": "idle"})

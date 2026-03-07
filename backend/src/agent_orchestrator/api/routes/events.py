"""Events stream endpoint (API-005)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.storage.event_log import EventLogReader, conversation_log_path

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/events")
def get_events(
    conversation_id: str | None = None,
    since: str | None = None,
) -> Any:
    """Return events for a conversation, optionally filtered by since event_id."""
    if conversation_id is None:
        return JSONResponse(
            status_code=400,
            content=error_response("conversation_id query parameter is required"),
        )

    log_path = conversation_log_path(conversation_id)
    reader = EventLogReader(log_path)

    if since is not None:
        events = reader.read_since(since)
    else:
        events = reader.read_all()

    # Sort by timestamp ascending
    events.sort(key=lambda e: e.get("timestamp", ""))

    return ok_response({"events": events})


@router.get("/events/latest")
def get_latest_events(
    conversation_id: str | None = None,
    n: int = 10,
) -> Any:
    """Return the last N events for a conversation."""
    if conversation_id is None:
        return JSONResponse(
            status_code=400,
            content=error_response("conversation_id query parameter is required"),
        )

    if n <= 0:
        return JSONResponse(
            status_code=400,
            content=error_response("n must be a positive integer"),
        )

    log_path = conversation_log_path(conversation_id)
    reader = EventLogReader(log_path)
    events = reader.tail(n)

    return ok_response({"events": events})

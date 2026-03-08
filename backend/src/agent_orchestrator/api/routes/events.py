"""Events stream endpoint (API-005 / T-204).

Primary source: SQLiteMessageEventRepository (DB).
Fallback: JSONL EventLogReader for legacy data.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.orchestrator.models import MessageEvent
from agent_orchestrator.storage.repositories.sqlite_message_event import (
    SQLiteMessageEventRepository,
)

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class AppendEventBody(BaseModel):
    conversation_id: str
    source_type: str
    text: str
    event_type: str
    source_id: str | None = None
    metadata_json: str = "{}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _event_to_dict(event: MessageEvent) -> dict[str, Any]:
    """Convert a MessageEvent dataclass to a JSON-safe dict."""
    return asdict(event)


def _get_repo() -> SQLiteMessageEventRepository:
    return SQLiteMessageEventRepository(get_db())


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/events")
def get_events(
    conversation_id: str | None = None,
    since: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Any:
    """Return events for a conversation from the DB, with pagination.

    Query parameters
    ----------------
    conversation_id : required
    since : optional event_id — return only events *after* this one
    limit : page size (default 100, max 1000)
    offset : number of rows to skip (default 0)
    """
    # Cap limit to prevent unbounded queries
    limit = max(1, min(limit, 1000))
    if conversation_id is None:
        return JSONResponse(
            status_code=400,
            content=error_response("conversation_id query parameter is required"),
        )

    repo = _get_repo()

    if since is not None:
        # Find the row id of the 'since' event, then fetch events after it.
        anchor = repo.get_by_event_id(since)
        if anchor is not None and anchor.id is not None:
            # Use raw query for "after anchor" with pagination.
            db = get_db()
            with db.connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM message_event "
                    "WHERE conversation_id = ? AND id > ? "
                    "ORDER BY id ASC "
                    "LIMIT ? OFFSET ?",
                    (conversation_id, anchor.id, limit, offset),
                ).fetchall()
            from agent_orchestrator.storage.repositories.sqlite_message_event import (
                _row_to_message_event,
            )

            events = [_event_to_dict(_row_to_message_event(r)) for r in rows]
        else:
            # Unknown since id — return all events (matches old JSONL behaviour).
            events = [
                _event_to_dict(e)
                for e in repo.list_by_conversation(conversation_id, limit=limit, offset=offset)
            ]
    else:
        events = [
            _event_to_dict(e)
            for e in repo.list_by_conversation(conversation_id, limit=limit, offset=offset)
        ]

    return ok_response({"events": events})


@router.get("/events/latest")
def get_latest_events(
    conversation_id: str | None = None,
    n: int = 10,
) -> Any:
    """Return the last N events for a conversation from the DB."""
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

    # Fetch the last N events by querying in descending order then reversing.
    db = get_db()
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT * FROM message_event "
            "WHERE conversation_id = ? "
            "ORDER BY id DESC "
            "LIMIT ?",
            (conversation_id, n),
        ).fetchall()

    from agent_orchestrator.storage.repositories.sqlite_message_event import (
        _row_to_message_event,
    )

    events = [_event_to_dict(_row_to_message_event(r)) for r in reversed(rows)]
    return ok_response({"events": events})


@router.post("/events")
def append_event(body: AppendEventBody) -> Any:
    """Append a new event to the conversation stream."""
    repo = _get_repo()
    now = datetime.now(UTC).isoformat()
    event = MessageEvent(
        conversation_id=body.conversation_id,
        event_id=str(uuid.uuid4()),
        source_type=body.source_type,
        text=body.text,
        event_type=body.event_type,
        created_at=now,
        source_id=body.source_id,
        metadata_json=body.metadata_json,
    )
    saved = repo.append(event)
    return ok_response({"event": _event_to_dict(saved)})

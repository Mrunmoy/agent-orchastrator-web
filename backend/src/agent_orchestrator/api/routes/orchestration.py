"""Orchestration control endpoints (API-003).

Provides run, continue, stop, and steer controls for batch orchestration.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.orchestrator.models import MessageEvent
from agent_orchestrator.storage.repositories.sqlite_message_event import (
    SQLiteMessageEventRepository,
)

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class RunBody(BaseModel):
    batch_size: int = 20

    @field_validator("batch_size")
    @classmethod
    def batch_size_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("batch_size must be >= 1")
        return v


class SteerBody(BaseModel):
    note: str

    @field_validator("note")
    @classmethod
    def note_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("note must not be empty")
        return v


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RUN_KEYS = [
    "id",
    "conversation_id",
    "status",
    "batch_size",
    "reason",
    "started_at",
    "ended_at",
    "created_at",
]


def _run_row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    d = dict(zip(_RUN_KEYS, row))
    # Computed fields expected by the frontend RunStatusData type
    d["run_id"] = d["id"]
    d["turns_completed"] = 0  # TODO: derive from message_event count
    d["turns_total"] = d.get("batch_size", 0)
    d["updated_at"] = d.get("ended_at") or d.get("started_at") or d.get("created_at")
    return d


_EVENT_KEYS = [
    "id",
    "conversation_id",
    "event_id",
    "source_type",
    "source_id",
    "text",
    "event_type",
    "metadata_json",
    "created_at",
]


def _event_row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(_EVENT_KEYS, row))


def _conversation_exists(conn: Any, conversation_id: str) -> bool:
    row = conn.execute(
        "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
        (conversation_id,),
    ).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Active run statuses (can be stopped)
# ---------------------------------------------------------------------------

_ACTIVE_STATUSES = ("running", "paused", "queued")

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.post("/orchestration/{conversation_id}/run")
def start_run(conversation_id: str, body: RunBody | None = None) -> Any:
    """Start a new batch run for a conversation."""
    batch_size = body.batch_size if body else 20
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )

        # Check for an already-active run (including paused)
        active = conn.execute(
            "SELECT id FROM scheduler_run "
            "WHERE conversation_id = ? AND status IN ('running', 'queued', 'paused') "
            "ORDER BY created_at DESC LIMIT 1",
            (conversation_id,),
        ).fetchone()
        if active is not None:
            return JSONResponse(
                status_code=409,
                content=error_response("A run is already active for this conversation"),
            )

        now = datetime.now(UTC).isoformat()
        run_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO scheduler_run "
            "(id, conversation_id, status, batch_size, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (run_id, conversation_id, "queued", batch_size, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM scheduler_run WHERE id = ?", (run_id,)).fetchone()
    return ok_response({"run": _run_row_to_dict(row)})


@router.post("/orchestration/{conversation_id}/continue")
def continue_run(conversation_id: str) -> Any:
    """Continue a paused batch run."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )

        paused = conn.execute(
            "SELECT id FROM scheduler_run "
            "WHERE conversation_id = ? AND status = 'paused' "
            "ORDER BY created_at DESC LIMIT 1",
            (conversation_id,),
        ).fetchone()
        if paused is None:
            return JSONResponse(
                status_code=409,
                content=error_response("No paused run to continue"),
            )

        run_id = paused[0]
        conn.execute(
            "UPDATE scheduler_run SET status = 'queued' WHERE id = ?",
            (run_id,),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM scheduler_run WHERE id = ?", (run_id,)).fetchone()
    return ok_response({"run": _run_row_to_dict(row)})


@router.post("/orchestration/{conversation_id}/stop")
def stop_run(conversation_id: str) -> Any:
    """Stop a running/paused/queued batch run."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )

        active = conn.execute(
            "SELECT id FROM scheduler_run "
            "WHERE conversation_id = ? AND status IN ('running', 'paused', 'queued') "
            "ORDER BY created_at DESC LIMIT 1",
            (conversation_id,),
        ).fetchone()
        if active is None:
            return JSONResponse(
                status_code=409,
                content=error_response("No active run to stop"),
            )

        run_id = active[0]
        now = datetime.now(UTC).isoformat()
        conn.execute(
            "UPDATE scheduler_run SET status = 'done', ended_at = ? WHERE id = ?",
            (now, run_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM scheduler_run WHERE id = ?", (run_id,)).fetchone()
    return ok_response({"run": _run_row_to_dict(row)})


@router.get("/orchestration/{conversation_id}/status")
def run_status(conversation_id: str) -> Any:
    """Return the latest scheduler_run for a conversation."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )

        row = conn.execute(
            "SELECT * FROM scheduler_run "
            "WHERE conversation_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (conversation_id,),
        ).fetchone()

    run = _run_row_to_dict(row) if row else None
    return ok_response({"run": run})


@router.get("/orchestration/{conversation_id}/runs")
def list_runs(conversation_id: str) -> Any:
    """List all runs for a conversation, most recent first."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )

        rows = conn.execute(
            "SELECT * FROM scheduler_run "
            "WHERE conversation_id = ? "
            "ORDER BY created_at DESC LIMIT 20",
            (conversation_id,),
        ).fetchall()

    runs = [_run_row_to_dict(row) for row in rows]
    return ok_response({"runs": runs})


@router.post("/orchestration/{conversation_id}/steer")
def steer(conversation_id: str, body: SteerBody) -> Any:
    """Inject a steering note into the conversation."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )

    now = datetime.now(UTC).isoformat()
    event = MessageEvent(
        conversation_id=conversation_id,
        event_id=str(uuid.uuid4()),
        source_type="user",
        text=body.note,
        event_type="steering",
        created_at=now,
    )
    repo = SQLiteMessageEventRepository(db)
    saved = repo.append(event)
    return ok_response({"event": asdict(saved)})

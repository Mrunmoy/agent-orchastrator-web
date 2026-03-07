"""Conversation CRUD endpoints (API-002)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.storage import DatabaseManager

# ---------------------------------------------------------------------------
# Module-level database (in-memory for now; replace with DI later)
# ---------------------------------------------------------------------------

_db: DatabaseManager | None = None


def _init_db() -> None:
    """(Re)initialise the module-level in-memory database."""
    global _db  # noqa: PLW0603
    if _db is not None:
        _db.close()
    _db = DatabaseManager(":memory:", check_same_thread=False)
    _db.initialize()


def get_db() -> DatabaseManager:
    """Return the module-level DatabaseManager, initialising if needed."""
    global _db  # noqa: PLW0603
    if _db is None:
        _init_db()
    assert _db is not None
    return _db


# Eagerly initialise on import so the router works immediately.
_init_db()

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class NewConversationBody(BaseModel):
    title: str
    project_path: str


class ConversationIdBody(BaseModel):
    conversation_id: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    keys = [
        "id",
        "title",
        "project_path",
        "state",
        "phase",
        "gate_status",
        "priority",
        "active",
        "summary_snapshot",
        "latest_artifact_id",
        "created_at",
        "updated_at",
        "deleted_at",
    ]
    return dict(zip(keys, row))


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/conversations")
def list_conversations() -> dict[str, Any]:
    """List all non-deleted conversations ordered by updated_at DESC."""
    db = get_db()
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT * FROM conversation " "WHERE deleted_at IS NULL " "ORDER BY updated_at DESC"
        ).fetchall()
    conversations = [_row_to_dict(r) for r in rows]
    return ok_response({"conversations": conversations})


@router.post("/conversations/new")
def create_conversation(body: NewConversationBody) -> dict[str, Any]:
    """Create a new conversation with sensible defaults."""
    now = datetime.now(UTC).isoformat()
    conv_id = str(uuid.uuid4())
    db = get_db()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO conversation "
            "(id, title, project_path, state, phase, gate_status, "
            " priority, active, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                conv_id,
                body.title,
                body.project_path,
                "debate",
                "design_debate",
                "open",
                100,
                0,
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM conversation WHERE id = ?", (conv_id,)).fetchone()
    return ok_response({"conversation": _row_to_dict(row)})


@router.post("/conversations/select")
def select_conversation(body: ConversationIdBody) -> Any:
    """Set one conversation as active, deactivating all others."""
    db = get_db()
    with db.connection() as conn:
        row = conn.execute(
            "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
            (body.conversation_id,),
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
        now = datetime.now(UTC).isoformat()
        conn.execute("UPDATE conversation SET active = 0, updated_at = ?", (now,))
        conn.execute(
            "UPDATE conversation SET active = 1, updated_at = ? WHERE id = ?",
            (now, body.conversation_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM conversation WHERE id = ?",
            (body.conversation_id,),
        ).fetchone()
    return ok_response({"conversation": _row_to_dict(updated)})


@router.post("/conversations/delete")
def delete_conversation(body: ConversationIdBody) -> Any:
    """Soft-delete a conversation by setting deleted_at."""
    db = get_db()
    with db.connection() as conn:
        row = conn.execute(
            "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
            (body.conversation_id,),
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
        now = datetime.now(UTC).isoformat()
        conn.execute(
            "UPDATE conversation SET deleted_at = ?, updated_at = ? WHERE id = ?",
            (now, now, body.conversation_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM conversation WHERE id = ?",
            (body.conversation_id,),
        ).fetchone()
    return ok_response({"conversation": _row_to_dict(updated)})


@router.post("/conversations/clear-all")
def clear_all_conversations() -> dict[str, Any]:
    """Soft-delete all non-deleted conversations. Return count."""
    db = get_db()
    with db.connection() as conn:
        now = datetime.now(UTC).isoformat()
        cur = conn.execute(
            "UPDATE conversation SET deleted_at = ?, updated_at = ? " "WHERE deleted_at IS NULL",
            (now, now),
        )
        conn.commit()
    return ok_response({"deleted_count": cur.rowcount})

"""SQLite implementation of ConversationRepository (T-104)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from agent_orchestrator.orchestrator.models import (
    Conversation,
    ConversationState,
    GateStatus,
    Phase,
)
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.conversation import ConversationRepository

# Column order from SELECT * on the conversation table.
_COLUMNS = [
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


def _row_to_conversation(row: tuple[Any, ...]) -> Conversation:
    """Map a raw SQLite row to a Conversation dataclass."""
    d = dict(zip(_COLUMNS, row))
    return Conversation(
        id=d["id"],
        title=d["title"],
        project_path=d["project_path"],
        state=ConversationState(d["state"]),
        phase=Phase(d["phase"]),
        gate_status=GateStatus(d["gate_status"]),
        priority=d["priority"],
        active=d["active"],
        summary_snapshot=d["summary_snapshot"],
        latest_artifact_id=d["latest_artifact_id"],
        created_at=d["created_at"],
        updated_at=d["updated_at"],
        deleted_at=d["deleted_at"],
    )


class SQLiteConversationRepository(ConversationRepository):
    """SQLite-backed conversation repository.

    Parameters
    ----------
    db:
        A ``DatabaseManager`` instance used to obtain connections.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self, title: str, project_path: str) -> Conversation:
        now = datetime.now(UTC).isoformat()
        conv_id = str(uuid.uuid4())
        with self._db.connection() as conn:
            conn.execute(
                "INSERT INTO conversation "
                "(id, title, project_path, state, phase, gate_status, "
                " priority, active, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    conv_id,
                    title,
                    project_path,
                    ConversationState.DEBATE.value,
                    Phase.DESIGN_DEBATE.value,
                    GateStatus.OPEN.value,
                    100,
                    0,
                    now,
                    now,
                ),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM conversation WHERE id = ?", (conv_id,)).fetchone()
        return _row_to_conversation(row)

    def get_by_id(self, conversation_id: str) -> Conversation | None:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM conversation WHERE id = ?", (conversation_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_conversation(row)

    def list_active(self) -> list[Conversation]:
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM conversation "
                "WHERE deleted_at IS NULL "
                "ORDER BY updated_at DESC"
            ).fetchall()
        return [_row_to_conversation(r) for r in rows]

    def update(self, conversation_id: str, fields: dict[str, Any]) -> Conversation:
        if not fields:
            conv = self.get_by_id(conversation_id)
            if conv is None:
                raise ValueError(f"Conversation {conversation_id} not found")
            return conv

        with self._db.connection() as conn:
            # Check existence first
            existing = conn.execute(
                "SELECT id FROM conversation WHERE id = ?", (conversation_id,)
            ).fetchone()
            if existing is None:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Always bump updated_at
            if "updated_at" not in fields:
                fields["updated_at"] = datetime.now(UTC).isoformat()

            set_clause = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [conversation_id]
            conn.execute(
                f"UPDATE conversation SET {set_clause} WHERE id = ?",  # noqa: S608
                values,
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM conversation WHERE id = ?", (conversation_id,)
            ).fetchone()
        return _row_to_conversation(row)

    def soft_delete(self, conversation_id: str) -> Conversation | None:
        with self._db.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
                (conversation_id,),
            ).fetchone()
            if existing is None:
                return None
            now = datetime.now(UTC).isoformat()
            conn.execute(
                "UPDATE conversation SET deleted_at = ?, updated_at = ? WHERE id = ?",
                (now, now, conversation_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM conversation WHERE id = ?", (conversation_id,)
            ).fetchone()
        return _row_to_conversation(row)

    def clear_all(self) -> int:
        with self._db.connection() as conn:
            now = datetime.now(UTC).isoformat()
            cur = conn.execute(
                "UPDATE conversation SET deleted_at = ?, updated_at = ? "
                "WHERE deleted_at IS NULL",
                (now, now),
            )
            conn.commit()
        return cur.rowcount

    def select(self, conversation_id: str) -> Conversation | None:
        with self._db.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
                (conversation_id,),
            ).fetchone()
            if existing is None:
                return None
            now = datetime.now(UTC).isoformat()
            # Atomic: deactivate all, then activate target
            conn.execute(
                "UPDATE conversation SET active = 0 " "WHERE deleted_at IS NULL AND id != ?",
                (conversation_id,),
            )
            conn.execute(
                "UPDATE conversation SET active = 1, updated_at = ? "
                "WHERE id = ? AND deleted_at IS NULL",
                (now, conversation_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM conversation WHERE id = ?", (conversation_id,)
            ).fetchone()
        return _row_to_conversation(row)

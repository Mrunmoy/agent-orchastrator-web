"""SQLite implementation of MessageEventRepository (T-108)."""

from __future__ import annotations

from typing import Any

from agent_orchestrator.orchestrator.models import MessageEvent
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.message_event import MessageEventRepository

# Column order from SELECT * on the message_event table.
_COLUMNS = [
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


def _row_to_message_event(row: tuple[Any, ...]) -> MessageEvent:
    """Map a raw SQLite row to a MessageEvent dataclass."""
    d = dict(zip(_COLUMNS, row))
    return MessageEvent(
        id=d["id"],
        conversation_id=d["conversation_id"],
        event_id=d["event_id"],
        source_type=d["source_type"],
        source_id=d["source_id"],
        text=d["text"],
        event_type=d["event_type"],
        metadata_json=d["metadata_json"],
        created_at=d["created_at"],
    )


class SQLiteMessageEventRepository(MessageEventRepository):
    """SQLite-backed message event repository (append-only).

    Parameters
    ----------
    db:
        A ``DatabaseManager`` instance used to obtain connections.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Append-only operations
    # ------------------------------------------------------------------

    def append(self, event: MessageEvent) -> MessageEvent:
        """Insert a new event and return it with the assigned autoincrement id."""
        with self._db.connection() as conn:
            conn.execute(
                "INSERT INTO message_event "
                "(conversation_id, event_id, source_type, source_id, "
                " text, event_type, metadata_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    event.conversation_id,
                    event.event_id,
                    event.source_type,
                    event.source_id,
                    event.text,
                    event.event_type,
                    event.metadata_json,
                    event.created_at,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM message_event WHERE event_id = ?",
                (event.event_id,),
            ).fetchone()
        return _row_to_message_event(row)

    def get_by_event_id(self, event_id: str) -> MessageEvent | None:
        """Return the event with the given event_id, or ``None``."""
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM message_event WHERE event_id = ?",
                (event_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_message_event(row)

    def list_by_conversation(
        self, conversation_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[MessageEvent]:
        """Return events for a conversation ordered by id, with pagination."""
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM message_event "
                "WHERE conversation_id = ? "
                "ORDER BY id ASC "
                "LIMIT ? OFFSET ?",
                (conversation_id, limit, offset),
            ).fetchall()
        return [_row_to_message_event(r) for r in rows]

    def list_by_type(
        self, conversation_id: str, event_type: str
    ) -> list[MessageEvent]:
        """Return events of a specific type within a conversation."""
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM message_event "
                "WHERE conversation_id = ? AND event_type = ? "
                "ORDER BY id ASC",
                (conversation_id, event_type),
            ).fetchall()
        return [_row_to_message_event(r) for r in rows]

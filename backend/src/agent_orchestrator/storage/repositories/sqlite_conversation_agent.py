"""SQLite implementation of ConversationAgentRepository (T-106).

Manages the ``conversation_agent`` join table: adding/removing agents,
reordering, and merge coordinator designation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.conversation_agent import (
    ConversationAgentRepository,
)

# Column order returned by ``SELECT * FROM conversation_agent``
_CA_COLUMNS = [
    "id",
    "conversation_id",
    "agent_id",
    "turn_order",
    "enabled",
    "permission_profile",
    "is_merge_coordinator",
    "created_at",
]


def _row_to_dict(row: tuple) -> dict[str, Any]:
    """Map a raw SQLite row to a dict."""
    return dict(zip(_CA_COLUMNS, row))


class SQLiteConversationAgentRepository(ConversationAgentRepository):
    """SQLite-backed conversation-agent join repository.

    Parameters
    ----------
    db:
        A :class:`DatabaseManager` that has already been initialised.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Add
    # ------------------------------------------------------------------

    def add_agent_to_conversation(
        self,
        conversation_id: str,
        agent_id: str,
        permission_profile: str = "default",
    ) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        ca_id = str(uuid.uuid4())

        with self._db.connection() as conn:
            # Determine next turn_order (max + 1, starting from 1)
            row = conn.execute(
                "SELECT COALESCE(MAX(turn_order), 0) FROM conversation_agent "
                "WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            next_order = row[0] + 1

            conn.execute(
                "INSERT INTO conversation_agent "
                "(id, conversation_id, agent_id, turn_order, enabled, "
                " permission_profile, is_merge_coordinator, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ca_id,
                    conversation_id,
                    agent_id,
                    next_order,
                    1,
                    permission_profile,
                    0,
                    now,
                ),
            )
            conn.commit()

            result_row = conn.execute(
                "SELECT * FROM conversation_agent WHERE id = ?", (ca_id,)
            ).fetchone()

        return _row_to_dict(result_row)

    # ------------------------------------------------------------------
    # Remove
    # ------------------------------------------------------------------

    def remove_agent(self, conversation_id: str, agent_id: str) -> None:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT id FROM conversation_agent "
                "WHERE conversation_id = ? AND agent_id = ?",
                (conversation_id, agent_id),
            ).fetchone()
            if row is None:
                raise KeyError(
                    f"Agent '{agent_id}' not linked to conversation '{conversation_id}'"
                )
            conn.execute(
                "DELETE FROM conversation_agent "
                "WHERE conversation_id = ? AND agent_id = ?",
                (conversation_id, agent_id),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_agents(self, conversation_id: str) -> list[dict[str, Any]]:
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM conversation_agent "
                "WHERE conversation_id = ? AND enabled = 1 "
                "ORDER BY turn_order ASC",
                (conversation_id,),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Reorder
    # ------------------------------------------------------------------

    def reorder(self, conversation_id: str, agent_ids: list[str]) -> None:
        with self._db.connection() as conn:
            # Verify the supplied ids match the current set
            rows = conn.execute(
                "SELECT agent_id FROM conversation_agent "
                "WHERE conversation_id = ? AND enabled = 1",
                (conversation_id,),
            ).fetchall()
            current_ids = {r[0] for r in rows}
            requested_ids = set(agent_ids)

            if current_ids != requested_ids:
                raise ValueError(
                    "agent_ids must exactly match the conversation's current agents"
                )

            # Atomic update of turn_order (1-based)
            for idx, agent_id in enumerate(agent_ids, start=1):
                conn.execute(
                    "UPDATE conversation_agent SET turn_order = ? "
                    "WHERE conversation_id = ? AND agent_id = ?",
                    (idx, conversation_id, agent_id),
                )
            conn.commit()

    # ------------------------------------------------------------------
    # Merge coordinator
    # ------------------------------------------------------------------

    def set_merge_coordinator(self, conversation_id: str, agent_id: str) -> None:
        with self._db.connection() as conn:
            # Verify the agent is part of the conversation
            row = conn.execute(
                "SELECT id FROM conversation_agent "
                "WHERE conversation_id = ? AND agent_id = ?",
                (conversation_id, agent_id),
            ).fetchone()
            if row is None:
                raise KeyError(
                    f"Agent '{agent_id}' not linked to conversation '{conversation_id}'"
                )

            # Clear existing merge coordinator(s) for this conversation
            conn.execute(
                "UPDATE conversation_agent SET is_merge_coordinator = 0 "
                "WHERE conversation_id = ?",
                (conversation_id,),
            )
            # Set the new one
            conn.execute(
                "UPDATE conversation_agent SET is_merge_coordinator = 1 "
                "WHERE conversation_id = ? AND agent_id = ?",
                (conversation_id, agent_id),
            )
            conn.commit()

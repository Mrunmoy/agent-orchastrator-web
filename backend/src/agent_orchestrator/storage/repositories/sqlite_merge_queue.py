"""SQLite implementation of MergeQueueRepository (T-110).

Uses ``DatabaseManager`` for connection access. Merge-queue entries are
stored as dicts (no domain dataclass yet) following the ABC contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from agent_orchestrator.orchestrator.models import MergeQueueStatus
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.merge_queue import MergeQueueRepository


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_COLUMNS = (
    "id",
    "conversation_id",
    "task_id",
    "pr_number",
    "pr_url",
    "pr_branch",
    "author_agent_id",
    "reviewer_agent_id",
    "position",
    "status",
    "queued_at",
    "merged_at",
    "created_at",
)


def _row_to_dict(row: tuple, description: tuple) -> dict[str, Any]:
    """Map a raw SQLite row to a dict."""
    col_names = [col[0] for col in description]
    return dict(zip(col_names, row))


class SQLiteMergeQueueRepository(MergeQueueRepository):
    """SQLite-backed merge-queue CRUD repository.

    Parameters
    ----------
    db:
        A ``DatabaseManager`` instance providing connection access.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def enqueue(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Add a new entry to the merge queue.

        Required keys in *entry*: ``conversation_id``, ``task_id``,
        ``author_agent_id``.  Optional: ``pr_number``, ``pr_url``,
        ``pr_branch``.

        Position is auto-assigned as max(existing positions for this
        conversation) + 1.
        """
        entry_id = str(uuid.uuid4())
        now = _now_iso()
        conversation_id = entry["conversation_id"]

        with self._db.connection() as conn:
            # Determine next position for this conversation.
            cur = conn.execute(
                "SELECT COALESCE(MAX(position), 0) FROM merge_queue "
                "WHERE conversation_id = ?",
                (conversation_id,),
            )
            max_pos = cur.fetchone()[0]
            position = max_pos + 1

            conn.execute(
                """INSERT INTO merge_queue
                   (id, conversation_id, task_id, pr_number, pr_url, pr_branch,
                    author_agent_id, reviewer_agent_id, position, status,
                    queued_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entry_id,
                    conversation_id,
                    entry["task_id"],
                    entry.get("pr_number"),
                    entry.get("pr_url"),
                    entry.get("pr_branch"),
                    entry["author_agent_id"],
                    entry.get("reviewer_agent_id"),
                    position,
                    MergeQueueStatus.QUEUED.value,
                    now,
                    now,
                ),
            )
            conn.commit()

        return {
            "id": entry_id,
            "conversation_id": conversation_id,
            "task_id": entry["task_id"],
            "pr_number": entry.get("pr_number"),
            "pr_url": entry.get("pr_url"),
            "pr_branch": entry.get("pr_branch"),
            "author_agent_id": entry["author_agent_id"],
            "reviewer_agent_id": entry.get("reviewer_agent_id"),
            "position": position,
            "status": MergeQueueStatus.QUEUED.value,
            "queued_at": now,
            "merged_at": None,
            "created_at": now,
        }

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, entry_id: str) -> dict[str, Any] | None:
        with self._db.connection() as conn:
            conn.row_factory = None
            cur = conn.execute("SELECT * FROM merge_queue WHERE id = ?", (entry_id,))
            row = cur.fetchone()
        if row is None:
            return None
        return _row_to_dict(row, cur.description)

    def list_by_conversation(self, conversation_id: str) -> list[dict[str, Any]]:
        with self._db.connection() as conn:
            conn.row_factory = None
            cur = conn.execute(
                "SELECT * FROM merge_queue WHERE conversation_id = ? "
                "ORDER BY position ASC",
                (conversation_id,),
            )
            rows = cur.fetchall()
            desc = cur.description
        return [_row_to_dict(row, desc) for row in rows]

    def get_current_merging(self, conversation_id: str) -> dict[str, Any] | None:
        with self._db.connection() as conn:
            conn.row_factory = None
            cur = conn.execute(
                "SELECT * FROM merge_queue "
                "WHERE conversation_id = ? AND status = ? "
                "LIMIT 1",
                (conversation_id, MergeQueueStatus.MERGING.value),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return _row_to_dict(row, cur.description)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_status(self, entry_id: str, status: str) -> bool:
        """Update the status of a queue entry.

        Enforces: only one entry can have status ``'merging'`` at a time
        per conversation.
        """
        with self._db.connection() as conn:
            conn.row_factory = None

            # Look up existing entry.
            cur = conn.execute(
                "SELECT conversation_id, status FROM merge_queue WHERE id = ?",
                (entry_id,),
            )
            row = cur.fetchone()
            if row is None:
                return False

            conversation_id = row[0]

            # Enforce single-merging constraint.
            if status == MergeQueueStatus.MERGING.value:
                cur2 = conn.execute(
                    "SELECT id FROM merge_queue "
                    "WHERE conversation_id = ? AND status = ? AND id != ?",
                    (conversation_id, MergeQueueStatus.MERGING.value, entry_id),
                )
                if cur2.fetchone() is not None:
                    raise ValueError(
                        f"Cannot set entry {entry_id} to 'merging': another entry "
                        f"in conversation {conversation_id} is already merging"
                    )

            updates: dict[str, Any] = {"status": status}
            if status == MergeQueueStatus.MERGED.value:
                updates["merged_at"] = _now_iso()

            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [entry_id]

            conn.execute(f"UPDATE merge_queue SET {set_clause} WHERE id = ?", values)
            conn.commit()

        return True

    def assign_reviewer(self, entry_id: str, reviewer_agent_id: str) -> bool:
        with self._db.connection() as conn:
            cur = conn.execute(
                "UPDATE merge_queue SET reviewer_agent_id = ? WHERE id = ?",
                (reviewer_agent_id, entry_id),
            )
            conn.commit()
        return cur.rowcount > 0

    def reorder(self, conversation_id: str, ordered_ids: list[str]) -> bool:
        """Reorder queue entries by assigning positions 1..N based on list order."""
        with self._db.connection() as conn:
            for position, entry_id in enumerate(ordered_ids, start=1):
                conn.execute(
                    "UPDATE merge_queue SET position = ? "
                    "WHERE id = ? AND conversation_id = ?",
                    (position, entry_id, conversation_id),
                )
            conn.commit()
        return True

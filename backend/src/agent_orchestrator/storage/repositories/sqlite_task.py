"""SQLite implementation of TaskRepository (T-107).

Uses ``DatabaseManager`` for connection access and stores ``depends_on``
as a JSON array of task IDs in the ``depends_on_json`` column.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from agent_orchestrator.orchestrator.models import Task, TaskStatus
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.task import TaskRepository


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteTaskRepository(TaskRepository):
    """SQLite-backed task CRUD repository.

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

    def create(
        self,
        conversation_id: str,
        title: str,
        spec_json: str,
        *,
        priority: int = 100,
        depends_on: list[str] | None = None,
    ) -> Task:
        task_id = str(uuid.uuid4())
        now = _now_iso()
        depends_on_json = json.dumps(depends_on or [])

        with self._db.connection() as conn:
            conn.execute(
                """INSERT INTO task
                   (id, conversation_id, title, spec_json, status, priority,
                    depends_on_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task_id,
                    conversation_id,
                    title,
                    spec_json,
                    TaskStatus.TODO.value,
                    priority,
                    depends_on_json,
                    now,
                    now,
                ),
            )
            conn.commit()

        return Task(
            id=task_id,
            conversation_id=conversation_id,
            title=title,
            spec_json=spec_json,
            status=TaskStatus.TODO,
            priority=priority,
            depends_on_json=depends_on_json,
            created_at=now,
            updated_at=now,
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, task_id: str) -> Task | None:
        with self._db.connection() as conn:
            conn.row_factory = None  # ensure tuple rows
            cur = conn.execute("SELECT * FROM task WHERE id = ?", (task_id,))
            row = cur.fetchone()
        if row is None:
            return None
        return self._row_to_task(row, cur.description)

    def list_by_conversation(
        self,
        conversation_id: str,
        *,
        status_filter: TaskStatus | None = None,
    ) -> list[Task]:
        sql = "SELECT * FROM task WHERE conversation_id = ?"
        params: list[str] = [conversation_id]
        if status_filter is not None:
            sql += " AND status = ?"
            params.append(status_filter.value)
        sql += " ORDER BY priority, created_at"

        with self._db.connection() as conn:
            conn.row_factory = None
            cur = conn.execute(sql, params)
            rows = cur.fetchall()
            desc = cur.description
        return [self._row_to_task(row, desc) for row in rows]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        # Validate enum membership (already enforced by type, but guard
        # against raw strings passed through untyped layers).
        if not isinstance(status, TaskStatus):
            raise ValueError(f"Invalid status: {status!r}")

        task = self.get_by_id(task_id)
        if task is None:
            raise KeyError(f"Task not found: {task_id}")

        # Dependency gate: cannot advance unless all deps are done.
        # (Skip the check for BLOCKED — you can always block a task.)
        if status != TaskStatus.BLOCKED:
            dep_ids: list[str] = json.loads(task.depends_on_json)
            if dep_ids:
                self._assert_all_deps_done(dep_ids, task_id)

        now = _now_iso()
        updates = {"status": status.value, "updated_at": now}

        # Track started/finished timestamps.
        if status != TaskStatus.TODO and task.started_at is None:
            updates["started_at"] = now
        if status in (TaskStatus.DONE, TaskStatus.BLOCKED):
            updates["finished_at"] = now

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [task_id]

        with self._db.connection() as conn:
            conn.execute(f"UPDATE task SET {set_clause} WHERE id = ?", values)
            conn.commit()

    def assign_owner(self, task_id: str, agent_id: str) -> None:
        with self._db.connection() as conn:
            cur = conn.execute(
                "UPDATE task SET owner_agent_id = ?, updated_at = ? WHERE id = ?",
                (agent_id, _now_iso(), task_id),
            )
            conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"Task not found: {task_id}")

    def update_result(
        self,
        task_id: str,
        result_summary: str,
        evidence_json: str,
    ) -> None:
        with self._db.connection() as conn:
            cur = conn.execute(
                "UPDATE task SET result_summary = ?, evidence_json = ?, updated_at = ? "
                "WHERE id = ?",
                (result_summary, evidence_json, _now_iso(), task_id),
            )
            conn.commit()
        if cur.rowcount == 0:
            raise KeyError(f"Task not found: {task_id}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _assert_all_deps_done(self, dep_ids: list[str], task_id: str) -> None:
        """Raise ``ValueError`` if any dependency task is not done."""
        placeholders = ", ".join("?" for _ in dep_ids)
        with self._db.connection() as conn:
            cur = conn.execute(
                f"SELECT id, status FROM task WHERE id IN ({placeholders})",
                dep_ids,
            )
            rows = cur.fetchall()

        found = {row[0]: row[1] for row in rows}
        for dep_id in dep_ids:
            dep_status = found.get(dep_id)
            if dep_status != TaskStatus.DONE.value:
                raise ValueError(
                    f"Cannot transition task {task_id} to implementing: "
                    f"dependency {dep_id} has status {dep_status!r} (expected 'done')"
                )

    @staticmethod
    def _row_to_task(row: tuple, description: tuple) -> Task:
        """Map a raw SQLite row to a ``Task`` dataclass."""
        col_names = [col[0] for col in description]
        data = dict(zip(col_names, row))
        return Task(
            id=data["id"],
            conversation_id=data["conversation_id"],
            title=data["title"],
            spec_json=data["spec_json"],
            status=TaskStatus(data["status"]),
            priority=data["priority"],
            owner_agent_id=data.get("owner_agent_id"),
            depends_on_json=data.get("depends_on_json", "[]"),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            result_summary=data.get("result_summary"),
            evidence_json=data.get("evidence_json", "[]"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

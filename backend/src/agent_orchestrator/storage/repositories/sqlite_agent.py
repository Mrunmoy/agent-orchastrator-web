"""SQLite implementation of AgentRepository (T-105).

Provides concrete CRUD operations for the ``agent`` table backed by
a :class:`DatabaseManager` connection.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from agent_orchestrator.orchestrator.models import Agent, AgentRole, AgentStatus, Provider
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.agent import AgentRepository

# Column order returned by ``SELECT * FROM agent``
_AGENT_COLUMNS = [
    "id",
    "display_name",
    "provider",
    "model",
    "personality_key",
    "role",
    "status",
    "session_id",
    "capabilities_json",
    "sort_order",
    "created_at",
    "updated_at",
]

# Columns that callers may update via ``update()``.
_UPDATABLE = {
    "display_name",
    "provider",
    "model",
    "role",
    "personality_key",
    "capabilities_json",
    "status",
    "session_id",
}

_VALID_PROVIDERS = {p.value for p in Provider}
_VALID_ROLES = {r.value for r in AgentRole}


def _row_to_agent(row: tuple) -> Agent:
    """Map a raw SQLite row (SELECT *) to an Agent dataclass."""
    d = dict(zip(_AGENT_COLUMNS, row))
    return Agent(
        id=d["id"],
        display_name=d["display_name"],
        provider=Provider(d["provider"]),
        model=d["model"],
        role=AgentRole(d["role"]),
        status=AgentStatus(d["status"]),
        capabilities_json=d["capabilities_json"],
        created_at=d["created_at"],
        updated_at=d["updated_at"],
        personality_key=d["personality_key"],
        session_id=d["session_id"],
    )


class SQLiteAgentRepository(AgentRepository):
    """SQLite-backed agent repository.

    Parameters
    ----------
    db:
        A :class:`DatabaseManager` that has already been initialised.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(
        self,
        display_name: str,
        provider: str,
        model: str,
        role: str,
        personality_key: str | None = None,
    ) -> Agent:
        if provider not in _VALID_PROVIDERS:
            raise ValueError(
                f"Invalid provider '{provider}'. "
                f"Valid providers: {sorted(_VALID_PROVIDERS)}"
            )
        if role not in _VALID_ROLES:
            raise ValueError(
                f"Invalid role '{role}'. Valid roles: {sorted(_VALID_ROLES)}"
            )

        now = datetime.now(UTC).isoformat()
        agent_id = str(uuid.uuid4())

        with self._db.connection() as conn:
            conn.execute(
                "INSERT INTO agent "
                "(id, display_name, provider, model, personality_key, role, "
                " status, session_id, capabilities_json, sort_order, "
                " created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    agent_id,
                    display_name,
                    provider,
                    model,
                    personality_key,
                    role,
                    "idle",
                    None,
                    "[]",
                    0,
                    now,
                    now,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM agent WHERE id = ?", (agent_id,)
            ).fetchone()

        return _row_to_agent(row)

    def get_by_id(self, agent_id: str) -> Agent | None:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM agent WHERE id = ?", (agent_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_agent(row)

    def list_all(self) -> list[Agent]:
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM agent ORDER BY sort_order ASC, display_name ASC"
            ).fetchall()
        return [_row_to_agent(r) for r in rows]

    def update(self, agent_id: str, fields: dict[str, object]) -> Agent:
        with self._db.connection() as conn:
            # Verify agent exists
            existing = conn.execute(
                "SELECT id FROM agent WHERE id = ?", (agent_id,)
            ).fetchone()
            if existing is None:
                raise KeyError(f"Agent '{agent_id}' not found")

            # Validate enum fields if present
            if "provider" in fields and fields["provider"] not in _VALID_PROVIDERS:
                raise ValueError(
                    f"Invalid provider '{fields['provider']}'. "
                    f"Valid providers: {sorted(_VALID_PROVIDERS)}"
                )
            if "role" in fields and fields["role"] not in _VALID_ROLES:
                raise ValueError(
                    f"Invalid role '{fields['role']}'. "
                    f"Valid roles: {sorted(_VALID_ROLES)}"
                )

            # Build SET clause from allowed fields
            sets: list[str] = []
            vals: list[object] = []
            for col, val in fields.items():
                if col in _UPDATABLE:
                    sets.append(f"{col} = ?")
                    vals.append(val)

            if sets:
                now = datetime.now(UTC).isoformat()
                sets.append("updated_at = ?")
                vals.append(now)
                vals.append(agent_id)
                conn.execute(
                    f"UPDATE agent SET {', '.join(sets)} WHERE id = ?",  # noqa: S608
                    vals,
                )
                conn.commit()

            row = conn.execute(
                "SELECT * FROM agent WHERE id = ?", (agent_id,)
            ).fetchone()

        return _row_to_agent(row)

    def delete(self, agent_id: str) -> None:
        with self._db.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM agent WHERE id = ?", (agent_id,)
            ).fetchone()
            if existing is None:
                raise KeyError(f"Agent '{agent_id}' not found")

            # Foreign key CASCADE should handle conversation_agent,
            # but explicit delete for safety with older schemas.
            conn.execute(
                "DELETE FROM conversation_agent WHERE agent_id = ?", (agent_id,)
            )
            conn.execute("DELETE FROM agent WHERE id = ?", (agent_id,))
            conn.commit()

    def update_sort_order(self, agent_id: str, order: int) -> None:
        with self._db.connection() as conn:
            existing = conn.execute(
                "SELECT id FROM agent WHERE id = ?", (agent_id,)
            ).fetchone()
            if existing is None:
                raise KeyError(f"Agent '{agent_id}' not found")

            now = datetime.now(UTC).isoformat()
            conn.execute(
                "UPDATE agent SET sort_order = ?, updated_at = ? WHERE id = ?",
                (order, now, agent_id),
            )
            conn.commit()

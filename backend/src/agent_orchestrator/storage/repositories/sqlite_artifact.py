"""SQLite implementation of ArtifactRepository (T-109)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from agent_orchestrator.orchestrator.models import Artifact, ArtifactType
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.artifact import ArtifactRepository

_COLUMNS = [
    "id",
    "conversation_id",
    "batch_id",
    "type",
    "payload_json",
    "created_at",
]


def _row_to_artifact(row: tuple[Any, ...]) -> Artifact:
    """Map a raw SQLite row to an Artifact dataclass."""
    d = dict(zip(_COLUMNS, row))
    return Artifact(
        id=d["id"],
        conversation_id=d["conversation_id"],
        type=ArtifactType(d["type"]),
        payload_json=d["payload_json"],
        created_at=d["created_at"],
        batch_id=d["batch_id"],
    )


class SQLiteArtifactRepository(ArtifactRepository):
    """SQLite-backed artifact repository.

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

    def create(self, artifact: Artifact) -> Artifact:
        now = datetime.now(UTC).isoformat()
        artifact_id = artifact.id or str(uuid.uuid4())
        created_at = artifact.created_at or now
        with self._db.connection() as conn:
            conn.execute(
                "INSERT INTO artifact "
                "(id, conversation_id, batch_id, type, payload_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    artifact_id,
                    artifact.conversation_id,
                    artifact.batch_id,
                    artifact.type.value if isinstance(artifact.type, ArtifactType) else artifact.type,
                    artifact.payload_json,
                    created_at,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM artifact WHERE id = ?", (artifact_id,)
            ).fetchone()
        return _row_to_artifact(row)

    def get_by_id(self, artifact_id: str) -> Artifact | None:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM artifact WHERE id = ?", (artifact_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_artifact(row)

    def list_by_conversation(
        self, conversation_id: str, *, type_filter: ArtifactType | None = None
    ) -> list[Artifact]:
        with self._db.connection() as conn:
            if type_filter is not None:
                rows = conn.execute(
                    "SELECT * FROM artifact "
                    "WHERE conversation_id = ? AND type = ? "
                    "ORDER BY created_at DESC",
                    (conversation_id, type_filter.value),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM artifact "
                    "WHERE conversation_id = ? "
                    "ORDER BY created_at DESC",
                    (conversation_id,),
                ).fetchall()
        return [_row_to_artifact(r) for r in rows]

    def get_latest(self, conversation_id: str) -> Artifact | None:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM artifact "
                "WHERE conversation_id = ? "
                "ORDER BY created_at DESC LIMIT 1",
                (conversation_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_artifact(row)

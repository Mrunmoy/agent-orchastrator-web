"""Database bootstrap loader and connection manager (DATA-002).

Provides ``DatabaseManager`` for initialising the SQLite schema and
obtaining connections with sensible defaults (WAL mode, foreign keys).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# Schema version embedded by this loader.  Bump when schema.sql changes.
_SCHEMA_VERSION = 5

# Migrations keyed by target version.  Each entry is a list of SQL statements
# that bring the schema from (version - 1) to version.
_MIGRATIONS: dict[int, list[str]] = {
    2: [
        ("ALTER TABLE agent ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"),
    ],
    3: [
        # Recreate conversation_agent with FK constraints and UNIQUE.
        # DROP + CREATE is safe because the table was unused before UI-014.
        "DROP TABLE IF EXISTS conversation_agent",
        """CREATE TABLE IF NOT EXISTS conversation_agent (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            agent_id TEXT NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
            turn_order INTEGER NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1,
            permission_profile TEXT NOT NULL DEFAULT 'default',
            is_merge_coordinator INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT '',
            UNIQUE (conversation_id, agent_id)
        )""",
    ],
    4: [
        """CREATE TABLE IF NOT EXISTS merge_queue (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            task_id TEXT NOT NULL REFERENCES task(id) ON DELETE CASCADE,
            pr_number INTEGER,
            pr_url TEXT,
            pr_branch TEXT,
            author_agent_id TEXT NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
            reviewer_agent_id TEXT,
            position INTEGER,
            status TEXT NOT NULL,
            queued_at TEXT,
            merged_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE INDEX IF NOT EXISTS idx_merge_queue_conversation
            ON merge_queue(conversation_id, status)""",
        """CREATE INDEX IF NOT EXISTS idx_merge_queue_status_position
            ON merge_queue(status, position)""",
    ],
    5: [
        # Clean up partial migration leftovers
        "DROP TABLE IF EXISTS task_new",
        "DROP TABLE IF EXISTS artifact_new",
        "DROP TABLE IF EXISTS message_event_new",
        # -- Recreate task with FK constraints --
        """CREATE TABLE IF NOT EXISTS task_new (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            spec_json TEXT NOT NULL,
            status TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 100,
            owner_agent_id TEXT REFERENCES agent(id) ON DELETE SET NULL,
            depends_on_json TEXT NOT NULL DEFAULT '[]',
            started_at TEXT,
            finished_at TEXT,
            result_summary TEXT,
            evidence_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""",
        "INSERT INTO task_new SELECT * FROM task",
        "DROP TABLE task",
        "ALTER TABLE task_new RENAME TO task",
        """CREATE INDEX IF NOT EXISTS idx_task_conversation_status
            ON task(conversation_id, status, priority)""",
        # -- Recreate artifact with FK constraint --
        """CREATE TABLE IF NOT EXISTS artifact_new (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            batch_id TEXT,
            type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""",
        "INSERT INTO artifact_new SELECT * FROM artifact",
        "DROP TABLE artifact",
        "ALTER TABLE artifact_new RENAME TO artifact",
        """CREATE INDEX IF NOT EXISTS idx_artifact_conversation_created
            ON artifact(conversation_id, created_at DESC)""",
        # -- Recreate message_event with FK constraints --
        """CREATE TABLE IF NOT EXISTS message_event_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            event_id TEXT NOT NULL UNIQUE,
            source_type TEXT NOT NULL,
            source_id TEXT REFERENCES agent(id) ON DELETE SET NULL,
            text TEXT NOT NULL,
            event_type TEXT NOT NULL,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        )""",
        "INSERT INTO message_event_new SELECT * FROM message_event",
        "DROP TABLE message_event",
        "ALTER TABLE message_event_new RENAME TO message_event",
        """CREATE INDEX IF NOT EXISTS idx_message_event_conversation
            ON message_event(conversation_id, id)""",
        # -- New index for SSE Last-Event-ID lookups --
        """CREATE INDEX IF NOT EXISTS idx_message_event_event_id
            ON message_event(event_id)""",
    ],
}


class DatabaseManager:
    """Manages a single SQLite database: bootstrap, versioning, connections.

    Parameters
    ----------
    db_path:
        Filesystem path to the SQLite file, or ``":memory:"`` for an
        in-memory database.
    """

    def __init__(
        self,
        db_path: str | Path,
        *,
        check_same_thread: bool = True,
    ) -> None:
        self._db_path = str(db_path)
        self._conn: sqlite3.Connection = sqlite3.connect(
            self._db_path, check_same_thread=check_same_thread
        )
        self._conn.execute("PRAGMA foreign_keys = ON")

    # ------------------------------------------------------------------
    # Schema bootstrap
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Apply *schema.sql* and record the schema version.

        This method is **idempotent** — calling it on an already-initialised
        database is safe because the DDL uses ``CREATE … IF NOT EXISTS``.
        """
        schema_sql = _SCHEMA_PATH.read_text()
        self._conn.executescript(schema_sql)
        # Re-enable foreign keys after executescript (implicit COMMIT resets)
        self._conn.execute("PRAGMA foreign_keys = ON")
        current = self._read_user_version()
        if current < _SCHEMA_VERSION:
            self._apply_migrations(current)
            self._conn.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")

    # ------------------------------------------------------------------
    # Connection access
    # ------------------------------------------------------------------

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Yield the managed connection.

        The caller is responsible for calling ``conn.commit()`` when
        appropriate.  The context manager does **not** auto-commit or
        rollback.
        """
        yield self._conn

    # ------------------------------------------------------------------
    # Version introspection
    # ------------------------------------------------------------------

    @property
    def schema_version(self) -> int:
        """Return the current ``PRAGMA user_version`` value."""
        return self._read_user_version()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_migrations(self, from_version: int) -> None:
        """Run incremental migrations from *from_version* to _SCHEMA_VERSION.

        Table-recreation migrations (v5+) are executed atomically via
        ``executescript`` to prevent partial-failure states (e.g. table
        dropped but rename not yet applied).  Simpler ADD COLUMN migrations
        use individual ``execute`` calls with idempotent error handling.
        """
        # Migrations that use table-recreation and MUST run atomically.
        _ATOMIC_VERSIONS = frozenset({5})

        for target in range(from_version + 1, _SCHEMA_VERSION + 1):
            stmts = _MIGRATIONS.get(target, [])
            if not stmts:
                continue
            if target in _ATOMIC_VERSIONS:
                script = "BEGIN;\n" + ";\n".join(stmts) + ";\nCOMMIT;"
                self._conn.executescript(script)
                # executescript issues implicit COMMIT that resets PRAGMAs
                self._conn.execute("PRAGMA foreign_keys = ON")
            else:
                for stmt in stmts:
                    try:
                        self._conn.execute(stmt)
                    except sqlite3.OperationalError:
                        # Column/table may already exist (idempotent).
                        pass
                self._conn.commit()

    def _read_user_version(self) -> int:
        cur = self._conn.execute("PRAGMA user_version")
        return cur.fetchone()[0]

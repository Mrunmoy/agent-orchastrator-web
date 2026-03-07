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
_SCHEMA_VERSION = 2

# Migrations keyed by target version.  Each entry is a list of SQL statements
# that bring the schema from (version - 1) to version.
_MIGRATIONS: dict[int, list[str]] = {
    2: [
        (
            "ALTER TABLE agent ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
        ),
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
        """Run incremental migrations from *from_version* to _SCHEMA_VERSION."""
        for target in range(from_version + 1, _SCHEMA_VERSION + 1):
            stmts = _MIGRATIONS.get(target, [])
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

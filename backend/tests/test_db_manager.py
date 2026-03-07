"""Tests for DatabaseManager (DATA-002).

Verifies bootstrap loader initializes the schema, tracks version,
provides connection management, and is idempotent.
"""

import sqlite3

import pytest

from agent_orchestrator.storage.db import DatabaseManager

EXPECTED_TABLES = [
    "agent",
    "artifact",
    "conversation",
    "conversation_agent",
    "message_event",
    "resource_snapshot",
    "scheduler_run",
    "task",
]


@pytest.fixture
def mem_db():
    """Create a DatabaseManager with an in-memory database."""
    mgr = DatabaseManager(":memory:")
    mgr.initialize()
    yield mgr
    mgr.close()


# --- Initialization ---


def test_initialize_creates_all_tables(mem_db):
    """All 8 schema tables should exist after initialize()."""
    with mem_db.connection() as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
    for table in EXPECTED_TABLES:
        assert table in tables, f"Table '{table}' missing after initialize()"


def test_schema_version_is_one(mem_db):
    """Schema version should be 1 after initialization."""
    assert mem_db.schema_version == 1


def test_initialize_is_idempotent():
    """Calling initialize() twice should not raise."""
    mgr = DatabaseManager(":memory:")
    mgr.initialize()
    mgr.initialize()  # second call must not fail
    assert mgr.schema_version == 1
    mgr.close()


def test_initialize_preserves_data():
    """Data inserted between two initialize() calls should survive."""
    mgr = DatabaseManager(":memory:")
    mgr.initialize()
    with mgr.connection() as conn:
        now = "2026-03-07T00:00:00Z"
        conn.execute(
            "INSERT INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            ("a1", "Agent", "claude", "opus-4", None, "worker", "idle", None, "[]", now, now),
        )
        conn.commit()
    mgr.initialize()  # re-initialize
    with mgr.connection() as conn:
        cur = conn.execute("SELECT count(*) FROM agent")
        assert cur.fetchone()[0] == 1
    mgr.close()


# --- Connection context manager ---


def test_connection_yields_sqlite3_connection(mem_db):
    """connection() should yield an sqlite3.Connection."""
    with mem_db.connection() as conn:
        assert isinstance(conn, sqlite3.Connection)


def test_connection_has_foreign_keys_enabled(mem_db):
    """Foreign keys should be enabled on yielded connections."""
    with mem_db.connection() as conn:
        cur = conn.execute("PRAGMA foreign_keys")
        assert cur.fetchone()[0] == 1


def test_connection_allows_queries(mem_db):
    """Should be able to run queries through the connection."""
    with mem_db.connection() as conn:
        cur = conn.execute("SELECT 1 + 1")
        assert cur.fetchone()[0] == 2


# --- WAL mode ---


def test_wal_mode_on_file_db(tmp_path):
    """WAL mode should be active on file-backed databases."""
    db_path = tmp_path / "test.db"
    mgr = DatabaseManager(str(db_path))
    mgr.initialize()
    with mgr.connection() as conn:
        cur = conn.execute("PRAGMA journal_mode")
        mode = cur.fetchone()[0]
    mgr.close()
    assert mode == "wal"


# --- Foreign keys after initialize ---


def test_foreign_keys_enabled_after_initialize():
    """Foreign keys must remain on after initialize() (executescript resets them)."""
    mgr = DatabaseManager(":memory:")
    mgr.initialize()
    with mgr.connection() as conn:
        cur = conn.execute("PRAGMA foreign_keys")
        assert cur.fetchone()[0] == 1
    mgr.close()


# --- Context manager protocol ---


def test_context_manager_closes_on_exit():
    """DatabaseManager can be used as a context manager."""
    with DatabaseManager(":memory:") as mgr:
        mgr.initialize()
        assert mgr.schema_version == 1
    with pytest.raises(Exception):
        with mgr.connection() as conn:
            conn.execute("SELECT 1")


# --- Path object acceptance ---


def test_accepts_path_object(tmp_path):
    """DatabaseManager should accept pathlib.Path, not just str."""
    db_path = tmp_path / "test_path.db"
    mgr = DatabaseManager(db_path)
    mgr.initialize()
    assert mgr.schema_version == 1
    mgr.close()


# --- Close ---


def test_close_closes_connection(mem_db):
    """After close(), the underlying connection should be unusable."""
    mem_db.close()
    with pytest.raises(Exception):
        with mem_db.connection() as conn:
            conn.execute("SELECT 1")


# --- Schema version edge cases ---


def test_schema_version_before_initialize():
    """Schema version should be 0 before initialize() is called."""
    mgr = DatabaseManager(":memory:")
    assert mgr.schema_version == 0
    mgr.close()


# --- Re-export from package ---


def test_database_manager_importable_from_storage():
    """DatabaseManager should be importable from agent_orchestrator.storage."""
    from agent_orchestrator.storage import DatabaseManager as StorageDatabaseManager

    assert StorageDatabaseManager is DatabaseManager

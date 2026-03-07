"""Tests for SQLite schema v1 (DATA-001).

Verifies that schema.sql loads without error, creates all expected tables
with correct columns, sets WAL mode, and creates required indexes.
"""

import sqlite3
from pathlib import Path

import pytest

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "agent_orchestrator" / "storage" / "schema.sql"
)

_INSERT_MSG_EVENT = (
    "INSERT INTO message_event"
    " (conversation_id, event_id, source_type,"
    " source_id, text, event_type, created_at)"
    " VALUES (?,?,?,?,?,?,?)"
)


@pytest.fixture
def db():
    """Create an in-memory SQLite database with the schema applied."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    yield conn
    conn.close()


# --- Schema loads without error ---


def test_schema_file_exists():
    assert SCHEMA_PATH.exists(), f"schema.sql not found at {SCHEMA_PATH}"


def test_schema_loads_cleanly(db):
    """Schema should apply without errors."""
    cur = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    assert len(tables) >= 7


# --- WAL mode ---


def test_wal_mode_pragma_present():
    """WAL pragma is in schema.sql (in-memory dbs report 'memory' so we check the SQL text)."""
    schema_sql = SCHEMA_PATH.read_text()
    assert "PRAGMA journal_mode = WAL" in schema_sql


def test_wal_mode_on_file_db(tmp_path):
    """WAL mode activates on file-backed databases."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    cur = conn.execute("PRAGMA journal_mode")
    mode = cur.fetchone()[0]
    conn.close()
    assert mode == "wal"


# --- All expected tables exist ---

EXPECTED_TABLES = [
    "agent",
    "conversation",
    "conversation_agent",
    "task",
    "artifact",
    "message_event",
    "scheduler_run",
    "resource_snapshot",
]


@pytest.mark.parametrize("table_name", EXPECTED_TABLES)
def test_table_exists(db, table_name):
    cur = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    assert cur.fetchone()[0] == 1, f"Table '{table_name}' missing"


# --- Column checks per table ---

EXPECTED_COLUMNS = {
    "agent": [
        "id",
        "display_name",
        "provider",
        "model",
        "personality_key",
        "role",
        "status",
        "session_id",
        "capabilities_json",
        "created_at",
        "updated_at",
    ],
    "conversation": [
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
    ],
    "conversation_agent": [
        "id",
        "conversation_id",
        "agent_id",
        "turn_order",
        "enabled",
        "permission_profile",
        "is_merge_coordinator",
        "created_at",
    ],
    "task": [
        "id",
        "conversation_id",
        "title",
        "spec_json",
        "status",
        "priority",
        "owner_agent_id",
        "depends_on_json",
        "started_at",
        "finished_at",
        "result_summary",
        "evidence_json",
        "created_at",
        "updated_at",
    ],
    "artifact": [
        "id",
        "conversation_id",
        "batch_id",
        "type",
        "payload_json",
        "created_at",
    ],
    "message_event": [
        "id",
        "conversation_id",
        "event_id",
        "source_type",
        "source_id",
        "text",
        "event_type",
        "metadata_json",
        "created_at",
    ],
    "scheduler_run": [
        "id",
        "conversation_id",
        "status",
        "batch_size",
        "reason",
        "started_at",
        "ended_at",
        "created_at",
    ],
    "resource_snapshot": [
        "id",
        "captured_at",
        "cpu_load_1m",
        "ram_used_mb",
        "ram_total_mb",
        "gpu_json",
        "agent_capacity_available",
    ],
}


@pytest.mark.parametrize("table_name", EXPECTED_COLUMNS.keys())
def test_table_columns(db, table_name):
    cur = db.execute(f"PRAGMA table_info({table_name})")  # noqa: S608
    actual_cols = [row[1] for row in cur.fetchall()]
    expected = EXPECTED_COLUMNS[table_name]
    assert (
        actual_cols == expected
    ), f"Column mismatch in '{table_name}': expected {expected}, got {actual_cols}"


# --- Index checks ---

EXPECTED_INDEXES = [
    "idx_conversation_updated_at",
    "idx_conversation_state_priority",
    "idx_task_conversation_status",
    "idx_message_event_conversation",
    "idx_artifact_conversation_created",
    "idx_scheduler_run_conversation_status",
]


@pytest.mark.parametrize("index_name", EXPECTED_INDEXES)
def test_index_exists(db, index_name):
    cur = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='index' AND name=?",
        (index_name,),
    )
    assert cur.fetchone()[0] == 1, f"Index '{index_name}' missing"


# --- Idempotency: schema can be applied twice ---


def test_schema_idempotent():
    conn = sqlite3.connect(":memory:")
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    conn.executescript(schema_sql)  # second apply should not fail
    cur = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
    assert cur.fetchone()[0] >= 7
    conn.close()


# --- Foreign key references: basic insert/reference integrity ---


def test_conversation_agent_references(db):
    """Insert valid agent + conversation, then link them via conversation_agent."""
    now = "2026-03-07T00:00:00Z"
    db.execute(
        "INSERT INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        ("a1", "Test Agent", "claude", "opus-4", None, "worker", "idle", None, "[]", now, now),
    )
    db.execute(
        "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "c1",
            "Test Conv",
            "/tmp",
            "debate",
            "design_debate",
            "open",
            100,
            1,
            None,
            None,
            now,
            now,
            None,
        ),
    )
    db.execute(
        "INSERT INTO conversation_agent VALUES (?,?,?,?,?,?,?,?)",
        ("ca1", "c1", "a1", 1, 1, "full", 0, now),
    )
    cur = db.execute("SELECT count(*) FROM conversation_agent WHERE conversation_id='c1'")
    assert cur.fetchone()[0] == 1


def test_message_event_autoincrement(db):
    """message_event.id should autoincrement."""
    now = "2026-03-07T00:00:00Z"
    db.execute(
        "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "c1",
            "Test",
            "/tmp",
            "debate",
            "design_debate",
            "open",
            100,
            0,
            None,
            None,
            now,
            now,
            None,
        ),
    )
    db.execute(
        _INSERT_MSG_EVENT,
        ("c1", "evt-1", "user", None, "hello", "message", now),
    )
    db.execute(
        _INSERT_MSG_EVENT,
        ("c1", "evt-2", "agent", "a1", "hi", "message", now),
    )
    cur = db.execute("SELECT id FROM message_event ORDER BY id")
    ids = [row[0] for row in cur.fetchall()]
    assert ids == [1, 2]


def test_event_id_unique_constraint(db):
    """event_id must be unique across message_event rows."""
    now = "2026-03-07T00:00:00Z"
    db.execute(
        "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "c1",
            "Test",
            "/tmp",
            "debate",
            "design_debate",
            "open",
            100,
            0,
            None,
            None,
            now,
            now,
            None,
        ),
    )
    db.execute(
        _INSERT_MSG_EVENT,
        ("c1", "evt-dup", "user", None, "hello", "message", now),
    )
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            _INSERT_MSG_EVENT,
            ("c1", "evt-dup", "user", None, "duplicate", "message", now),
        )

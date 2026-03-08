"""Tests for FK constraints on task, artifact, message_event (T-102).

Verifies that missing FK constraints are enforced after schema v5,
and that migration v5 preserves existing data.
"""

import sqlite3
from pathlib import Path

import pytest

from agent_orchestrator.storage.db import DatabaseManager

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "agent_orchestrator"
    / "storage"
    / "schema.sql"
)

NOW = "2026-03-07T00:00:00Z"


def _insert_agent(conn: sqlite3.Connection, agent_id: str = "a1") -> None:
    conn.execute(
        "INSERT INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (agent_id, "Agent", "claude", "opus-4", None, "worker", "idle", None, "[]", 0, NOW, NOW),
    )


def _insert_conversation(conn: sqlite3.Connection, conv_id: str = "c1") -> None:
    conn.execute(
        "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (conv_id, "Conv", "/tmp", "debate", "design_debate", "open", 100, 1, None, None, NOW, NOW, None),
    )


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def db():
    """In-memory DB with current schema (v5) and foreign keys ON."""
    mgr = DatabaseManager(":memory:")
    mgr.initialize()
    with mgr.connection() as conn:
        yield conn
    mgr.close()


# ── TT-102-01: task FK on conversation_id ───────────────────────────────


def test_task_invalid_conversation_id_raises(db):
    """Inserting a task with a non-existent conversation_id must raise IntegrityError."""
    _insert_agent(db, "a1")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "t1", "bad-conv", "Title", "{}", "todo", 100, "a1",
                "[]", None, None, None, "[]", NOW, NOW,
            ),
        )


def test_task_invalid_owner_agent_id_raises(db):
    """Inserting a task with a non-existent owner_agent_id must raise IntegrityError."""
    _insert_conversation(db, "c1")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "t1", "c1", "Title", "{}", "todo", 100, "bad-agent",
                "[]", None, None, None, "[]", NOW, NOW,
            ),
        )


def test_task_null_owner_agent_id_allowed(db):
    """owner_agent_id is nullable — NULL should be accepted."""
    _insert_conversation(db, "c1")
    db.execute(
        "INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "t1", "c1", "Title", "{}", "todo", 100, None,
            "[]", None, None, None, "[]", NOW, NOW,
        ),
    )
    cur = db.execute("SELECT id FROM task WHERE id='t1'")
    assert cur.fetchone() is not None


# ── TT-102-02: artifact FK on conversation_id ──────────────────────────


def test_artifact_invalid_conversation_id_raises(db):
    """Inserting an artifact with a non-existent conversation_id must raise IntegrityError."""
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO artifact VALUES (?,?,?,?,?,?)",
            ("art1", "bad-conv", None, "code", "{}", NOW),
        )


# ── TT-102-03: message_event FK on conversation_id and source_id ───────


def test_message_event_invalid_conversation_id_raises(db):
    """Inserting a message_event with a non-existent conversation_id must raise IntegrityError."""
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO message_event"
            " (conversation_id, event_id, source_type, source_id, text, event_type, created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            ("bad-conv", "evt-1", "agent", None, "hello", "message", NOW),
        )


def test_message_event_invalid_source_id_raises(db):
    """Inserting a message_event with a non-existent source_id must raise IntegrityError."""
    _insert_conversation(db, "c1")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO message_event"
            " (conversation_id, event_id, source_type, source_id, text, event_type, created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            ("c1", "evt-1", "agent", "bad-agent", "hello", "message", NOW),
        )


def test_message_event_null_source_id_allowed(db):
    """source_id is nullable — NULL should be accepted (e.g. user messages)."""
    _insert_conversation(db, "c1")
    db.execute(
        "INSERT INTO message_event"
        " (conversation_id, event_id, source_type, source_id, text, event_type, created_at)"
        " VALUES (?,?,?,?,?,?,?)",
        ("c1", "evt-1", "user", None, "hello", "message", NOW),
    )
    cur = db.execute("SELECT event_id FROM message_event WHERE event_id='evt-1'")
    assert cur.fetchone() is not None


# ── TT-102-04: migration v4 → v5 preserves data ────────────────────────


def test_migration_v4_to_v5_preserves_data(tmp_path):
    """Migrating from v4 to v5 should keep existing rows and add FK constraints."""
    from agent_orchestrator.storage.db import _SCHEMA_VERSION

    # Verify we are actually testing v5
    assert _SCHEMA_VERSION == 5, f"Expected schema version 5, got {_SCHEMA_VERSION}"

    db_path = tmp_path / "migrate.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")

    # Bootstrap at schema v4 by loading schema.sql then freezing version at 4.
    # We create the tables WITHOUT FK constraints to simulate old schema.
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS agent (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            personality_key TEXT,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            session_id TEXT,
            capabilities_json TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS conversation (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            project_path TEXT NOT NULL,
            state TEXT NOT NULL,
            phase TEXT NOT NULL,
            gate_status TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 100,
            active INTEGER NOT NULL DEFAULT 0,
            summary_snapshot TEXT,
            latest_artifact_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT
        );
        CREATE TABLE IF NOT EXISTS conversation_agent (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            agent_id TEXT NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
            turn_order INTEGER NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1,
            permission_profile TEXT NOT NULL DEFAULT 'default',
            is_merge_coordinator INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT '',
            UNIQUE (conversation_id, agent_id)
        );
        CREATE TABLE IF NOT EXISTS task (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            title TEXT NOT NULL,
            spec_json TEXT NOT NULL,
            status TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 100,
            owner_agent_id TEXT,
            depends_on_json TEXT NOT NULL DEFAULT '[]',
            started_at TEXT,
            finished_at TEXT,
            result_summary TEXT,
            evidence_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS artifact (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            batch_id TEXT,
            type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS message_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            event_id TEXT NOT NULL UNIQUE,
            source_type TEXT NOT NULL,
            source_id TEXT,
            text TEXT NOT NULL,
            event_type TEXT NOT NULL,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS scheduler_run (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            status TEXT NOT NULL,
            batch_size INTEGER NOT NULL,
            reason TEXT,
            started_at TEXT,
            ended_at TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS resource_snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            captured_at TEXT NOT NULL,
            cpu_load_1m REAL NOT NULL,
            ram_used_mb INTEGER NOT NULL,
            ram_total_mb INTEGER NOT NULL,
            gpu_json TEXT NOT NULL DEFAULT '[]',
            agent_capacity_available INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS merge_queue (
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
        );
        CREATE INDEX IF NOT EXISTS idx_conversation_updated_at ON conversation(updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_conversation_state_priority ON conversation(state, priority, updated_at DESC);
        CREATE INDEX IF NOT EXISTS idx_task_conversation_status ON task(conversation_id, status, priority);
        CREATE INDEX IF NOT EXISTS idx_message_event_conversation ON message_event(conversation_id, id);
        CREATE INDEX IF NOT EXISTS idx_artifact_conversation_created ON artifact(conversation_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_scheduler_run_conversation_status ON scheduler_run(conversation_id, status, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_merge_queue_conversation ON merge_queue(conversation_id, status);
        CREATE INDEX IF NOT EXISTS idx_merge_queue_status_position ON merge_queue(status, position);
        """
    )
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(f"PRAGMA user_version = 4")

    # Insert seed data in all three tables that will be recreated
    now = "2026-03-07T00:00:00Z"
    conn.execute(
        "INSERT INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("a1", "Agent", "claude", "opus-4", None, "worker", "idle", None, "[]", 0, now, now),
    )
    conn.execute(
        "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("c1", "Conv", "/tmp", "debate", "design_debate", "open", 100, 1, None, None, now, now, None),
    )
    conn.execute(
        "INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("t1", "c1", "Title", "{}", "todo", 100, "a1", "[]", None, None, None, "[]", now, now),
    )
    conn.execute(
        "INSERT INTO artifact VALUES (?,?,?,?,?,?)",
        ("art1", "c1", None, "code", "{}", now),
    )
    conn.execute(
        "INSERT INTO message_event"
        " (conversation_id, event_id, source_type, source_id, text, event_type, created_at)"
        " VALUES (?,?,?,?,?,?,?)",
        ("c1", "evt-1", "agent", "a1", "hello", "message", now),
    )
    conn.commit()
    conn.close()

    # Now open via DatabaseManager — should run migration v5
    mgr = DatabaseManager(str(db_path))
    mgr.initialize()
    assert mgr.schema_version == 5

    with mgr.connection() as conn:
        # Verify data survived
        assert conn.execute("SELECT count(*) FROM task").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM artifact").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM message_event").fetchone()[0] == 1

        # Verify FK constraints are now enforced
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("t2", "bad-conv", "T2", "{}", "todo", 100, None, "[]", None, None, None, "[]", now, now),
            )

        # Verify the event_id index exists
        cur = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='index' AND name='idx_message_event_event_id'"
        )
        assert cur.fetchone()[0] == 1

    mgr.close()


# ── Index on message_event(event_id) ────────────────────────────────────


def test_event_id_index_exists(db):
    """Index idx_message_event_event_id should exist for SSE Last-Event-ID lookups."""
    cur = db.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='index' AND name='idx_message_event_event_id'"
    )
    assert cur.fetchone()[0] == 1

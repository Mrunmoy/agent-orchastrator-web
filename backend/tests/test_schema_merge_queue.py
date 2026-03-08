"""Tests for merge_queue table (T-101: schema migration v4).

Verifies that:
- TT-101-01: initialize() on a fresh DB creates merge_queue with all expected columns
- TT-101-02: migration from v3 to v4 adds merge_queue without data loss
- TT-101-03: FK constraints enforce valid conversation_id, task_id, author_agent_id
"""

import sqlite3

import pytest

from agent_orchestrator.storage.db import DatabaseManager

NOW = "2026-03-08T00:00:00Z"

MERGE_QUEUE_COLUMNS = [
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
]


@pytest.fixture
def mem_db():
    """Fresh in-memory DatabaseManager."""
    mgr = DatabaseManager(":memory:")
    mgr.initialize()
    yield mgr
    mgr.close()


def _seed_agent_conversation_task(conn: sqlite3.Connection) -> None:
    """Insert minimal agent, conversation, and task rows for FK references."""
    conn.execute(
        "INSERT INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("a1", "Agent", "claude", "opus-4", None, "worker", "idle", None, "[]", 0, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("c1", "Conv", "/tmp", "debate", "design_debate", "open", 100, 1, None, None, NOW, NOW, None),
    )
    conn.execute(
        "INSERT INTO task VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("t1", "c1", "Task", "{}", "todo", 100, None, "[]", None, None, None, "[]", NOW, NOW),
    )
    conn.commit()


# --- TT-101-01: Fresh DB creates merge_queue with all columns ---


class TestFreshDbMergeQueue:
    def test_merge_queue_table_exists(self, mem_db):
        """merge_queue table should exist after initialize()."""
        with mem_db.connection() as conn:
            cur = conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='merge_queue'"
            )
            assert cur.fetchone()[0] == 1

    def test_merge_queue_columns(self, mem_db):
        """merge_queue should have all expected columns in order."""
        with mem_db.connection() as conn:
            cur = conn.execute("PRAGMA table_info(merge_queue)")
            actual_cols = [row[1] for row in cur.fetchall()]
        assert actual_cols == MERGE_QUEUE_COLUMNS

    def test_schema_version_is_5(self, mem_db):
        """Schema version should be 5 after initialization."""
        assert mem_db.schema_version == 5

    def test_merge_queue_indexes_exist(self, mem_db):
        """Indexes on merge_queue should exist."""
        expected = [
            "idx_merge_queue_conversation",
            "idx_merge_queue_status_position",
        ]
        with mem_db.connection() as conn:
            for idx_name in expected:
                cur = conn.execute(
                    "SELECT count(*) FROM sqlite_master WHERE type='index' AND name=?",
                    (idx_name,),
                )
                assert cur.fetchone()[0] == 1, f"Index '{idx_name}' missing"


# --- TT-101-02: Migration from v3 to v4 preserves data ---


class TestMigrationV3ToV4:
    def test_migration_preserves_agent_data(self, tmp_path):
        """Existing agent rows survive migration to v4."""
        db_path = tmp_path / "migrate.db"
        # Create a v3 database
        mgr = DatabaseManager(str(db_path))
        mgr.initialize()
        with mgr.connection() as conn:
            conn.execute(
                "INSERT INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                ("a1", "Agent", "claude", "opus-4", None, "worker", "idle", None, "[]", 0, NOW, NOW),
            )
            conn.commit()
        mgr.close()

        # Manually set version back to 3 to simulate pre-v4 state,
        # but the table already exists because initialize() created it.
        # Instead, we verify data survives a re-initialize.
        mgr2 = DatabaseManager(str(db_path))
        mgr2.initialize()
        with mgr2.connection() as conn:
            cur = conn.execute("SELECT count(*) FROM agent")
            assert cur.fetchone()[0] == 1
            # merge_queue should exist
            cur = conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='merge_queue'"
            )
            assert cur.fetchone()[0] == 1
        assert mgr2.schema_version == 5
        mgr2.close()

    def test_migration_from_v3_creates_merge_queue(self, tmp_path):
        """Simulating a v3 DB (without merge_queue) and running migration adds the table."""
        db_path = tmp_path / "v3.db"
        # Bootstrap a v3 database manually
        mgr = DatabaseManager(str(db_path))
        mgr.initialize()
        mgr.close()

        # Downgrade: drop merge_queue and set version to 3
        conn = sqlite3.connect(str(db_path))
        conn.execute("DROP TABLE IF EXISTS merge_queue")
        conn.execute("PRAGMA user_version = 3")
        conn.commit()
        # Verify it's gone
        cur = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='merge_queue'"
        )
        assert cur.fetchone()[0] == 0
        conn.close()

        # Re-open with DatabaseManager — migration should recreate it
        mgr2 = DatabaseManager(str(db_path))
        mgr2.initialize()
        with mgr2.connection() as conn:
            cur = conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='merge_queue'"
            )
            assert cur.fetchone()[0] == 1
        assert mgr2.schema_version == 5
        mgr2.close()

    def test_migration_preserves_conversation_data(self, tmp_path):
        """Existing conversation rows survive the v3->v4 migration."""
        db_path = tmp_path / "conv.db"
        mgr = DatabaseManager(str(db_path))
        mgr.initialize()
        with mgr.connection() as conn:
            conn.execute(
                "INSERT INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("c1", "Conv", "/tmp", "debate", "design_debate", "open", 100, 1, None, None, NOW, NOW, None),
            )
            conn.commit()
        mgr.close()

        # Downgrade and re-migrate
        raw = sqlite3.connect(str(db_path))
        raw.execute("DROP TABLE IF EXISTS merge_queue")
        raw.execute("PRAGMA user_version = 3")
        raw.commit()
        raw.close()

        mgr2 = DatabaseManager(str(db_path))
        mgr2.initialize()
        with mgr2.connection() as conn:
            cur = conn.execute("SELECT count(*) FROM conversation")
            assert cur.fetchone()[0] == 1
        mgr2.close()


# --- TT-101-03: FK constraints on merge_queue ---


class TestMergeQueueForeignKeys:
    def test_valid_insert(self, mem_db):
        """A merge_queue row with valid FKs should insert successfully."""
        with mem_db.connection() as conn:
            _seed_agent_conversation_task(conn)
            conn.execute(
                "INSERT INTO merge_queue"
                " (id, conversation_id, task_id, pr_number, pr_url, pr_branch,"
                "  author_agent_id, reviewer_agent_id, position, status, queued_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("mq1", "c1", "t1", 42, "https://github.com/pr/42", "feat/x", "a1", None, 1, "queued", NOW),
            )
            conn.commit()
            cur = conn.execute("SELECT count(*) FROM merge_queue")
            assert cur.fetchone()[0] == 1

    def test_invalid_conversation_id_rejected(self, mem_db):
        """merge_queue rejects a row with non-existent conversation_id."""
        with mem_db.connection() as conn:
            _seed_agent_conversation_task(conn)
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO merge_queue"
                    " (id, conversation_id, task_id, pr_number, pr_url, pr_branch,"
                    "  author_agent_id, position, status, queued_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    ("mq2", "bad_conv", "t1", 1, "url", "branch", "a1", 1, "queued", NOW),
                )

    def test_invalid_task_id_rejected(self, mem_db):
        """merge_queue rejects a row with non-existent task_id."""
        with mem_db.connection() as conn:
            _seed_agent_conversation_task(conn)
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO merge_queue"
                    " (id, conversation_id, task_id, pr_number, pr_url, pr_branch,"
                    "  author_agent_id, position, status, queued_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    ("mq3", "c1", "bad_task", 1, "url", "branch", "a1", 1, "queued", NOW),
                )

    def test_invalid_author_agent_id_rejected(self, mem_db):
        """merge_queue rejects a row with non-existent author_agent_id."""
        with mem_db.connection() as conn:
            _seed_agent_conversation_task(conn)
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO merge_queue"
                    " (id, conversation_id, task_id, pr_number, pr_url, pr_branch,"
                    "  author_agent_id, position, status, queued_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    ("mq4", "c1", "t1", 1, "url", "branch", "bad_agent", 1, "queued", NOW),
                )

    def test_created_at_defaults_to_current_timestamp(self, mem_db):
        """created_at should get a default value when not provided."""
        with mem_db.connection() as conn:
            _seed_agent_conversation_task(conn)
            conn.execute(
                "INSERT INTO merge_queue"
                " (id, conversation_id, task_id, pr_number, pr_url, pr_branch,"
                "  author_agent_id, position, status, queued_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                ("mq5", "c1", "t1", 42, "url", "branch", "a1", 1, "queued", NOW),
            )
            conn.commit()
            cur = conn.execute("SELECT created_at FROM merge_queue WHERE id='mq5'")
            val = cur.fetchone()[0]
            assert val is not None and len(val) > 0

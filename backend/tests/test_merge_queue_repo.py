"""Tests for SQLiteMergeQueueRepository (T-110).

TDD test cases verifying CRUD operations and merge-queue constraints.
"""

from __future__ import annotations

import pytest

from agent_orchestrator.orchestrator.models import MergeQueueStatus
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_merge_queue import (
    SQLiteMergeQueueRepository,
)


def _seed_data(db: DatabaseManager) -> dict:
    """Insert minimal FK parents so merge_queue inserts succeed."""
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO agent (id, display_name, provider, model, role, status, "
            "capabilities_json, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "agent-1",
                "Claude",
                "claude",
                "opus",
                "worker",
                "idle",
                "[]",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.execute(
            "INSERT INTO agent (id, display_name, provider, model, role, status, "
            "capabilities_json, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "agent-2",
                "Codex",
                "codex",
                "codex-1",
                "worker",
                "idle",
                "[]",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.execute(
            "INSERT INTO conversation (id, title, project_path, state, phase, "
            "gate_status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "conv-1",
                "Test Conv",
                "/tmp",
                "debate",
                "design_debate",
                "open",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.execute(
            "INSERT INTO task (id, conversation_id, title, spec_json, status, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "task-1",
                "conv-1",
                "Task 1",
                "{}",
                "todo",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.execute(
            "INSERT INTO task (id, conversation_id, title, spec_json, status, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "task-2",
                "conv-1",
                "Task 2",
                "{}",
                "todo",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.execute(
            "INSERT INTO task (id, conversation_id, title, spec_json, status, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "task-3",
                "conv-1",
                "Task 3",
                "{}",
                "todo",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.commit()

    return {
        "conversation_id": "conv-1",
        "agent_id": "agent-1",
        "reviewer_agent_id": "agent-2",
        "task_ids": ["task-1", "task-2", "task-3"],
    }


@pytest.fixture
def repo():
    """Create an in-memory DB with schema and return a SQLiteMergeQueueRepository."""
    db = DatabaseManager(":memory:")
    db.initialize()
    _seed_data(db)
    yield SQLiteMergeQueueRepository(db)
    db.close()


def _make_entry(
    conversation_id: str = "conv-1",
    task_id: str = "task-1",
    author_agent_id: str = "agent-1",
    **kwargs,
) -> dict:
    return {
        "conversation_id": conversation_id,
        "task_id": task_id,
        "author_agent_id": author_agent_id,
        **kwargs,
    }


# ------------------------------------------------------------------
# TT-110-01: enqueue auto-assigns position as max(existing)+1
# ------------------------------------------------------------------


class TestEnqueuePosition:
    def test_first_entry_gets_position_1(self, repo: SQLiteMergeQueueRepository):
        result = repo.enqueue(_make_entry(task_id="task-1"))
        assert result["position"] == 1

    def test_second_entry_gets_position_2(self, repo: SQLiteMergeQueueRepository):
        repo.enqueue(_make_entry(task_id="task-1"))
        result = repo.enqueue(_make_entry(task_id="task-2"))
        assert result["position"] == 2

    def test_third_entry_gets_position_3(self, repo: SQLiteMergeQueueRepository):
        repo.enqueue(_make_entry(task_id="task-1"))
        repo.enqueue(_make_entry(task_id="task-2"))
        result = repo.enqueue(_make_entry(task_id="task-3"))
        assert result["position"] == 3

    def test_enqueue_returns_dict_with_id(self, repo: SQLiteMergeQueueRepository):
        result = repo.enqueue(_make_entry(task_id="task-1"))
        assert "id" in result
        assert len(result["id"]) == 36  # UUID format

    def test_enqueue_sets_queued_status(self, repo: SQLiteMergeQueueRepository):
        result = repo.enqueue(_make_entry(task_id="task-1"))
        assert result["status"] == MergeQueueStatus.QUEUED.value

    def test_enqueue_stores_optional_pr_fields(self, repo: SQLiteMergeQueueRepository):
        result = repo.enqueue(
            _make_entry(
                task_id="task-1",
                pr_number=42,
                pr_url="https://github.com/org/repo/pull/42",
                pr_branch="feature/foo",
            )
        )
        assert result["pr_number"] == 42
        assert result["pr_url"] == "https://github.com/org/repo/pull/42"
        assert result["pr_branch"] == "feature/foo"

    def test_enqueue_persists_and_retrievable(self, repo: SQLiteMergeQueueRepository):
        result = repo.enqueue(_make_entry(task_id="task-1"))
        fetched = repo.get_by_id(result["id"])
        assert fetched is not None
        assert fetched["id"] == result["id"]
        assert fetched["position"] == 1


# ------------------------------------------------------------------
# TT-110-02: update_status to 'merging' fails if another entry
#             is already 'merging'
# ------------------------------------------------------------------


class TestUpdateStatusMergingConstraint:
    def test_update_to_merging_succeeds_when_none_merging(
        self, repo: SQLiteMergeQueueRepository
    ):
        entry = repo.enqueue(_make_entry(task_id="task-1"))
        assert repo.update_status(entry["id"], MergeQueueStatus.MERGING.value)
        fetched = repo.get_by_id(entry["id"])
        assert fetched is not None
        assert fetched["status"] == MergeQueueStatus.MERGING.value

    def test_update_to_merging_fails_when_another_is_merging(
        self, repo: SQLiteMergeQueueRepository
    ):
        entry1 = repo.enqueue(_make_entry(task_id="task-1"))
        entry2 = repo.enqueue(_make_entry(task_id="task-2"))
        repo.update_status(entry1["id"], MergeQueueStatus.MERGING.value)

        with pytest.raises(ValueError, match="already merging"):
            repo.update_status(entry2["id"], MergeQueueStatus.MERGING.value)

    def test_update_to_merging_succeeds_after_previous_merged(
        self, repo: SQLiteMergeQueueRepository
    ):
        entry1 = repo.enqueue(_make_entry(task_id="task-1"))
        entry2 = repo.enqueue(_make_entry(task_id="task-2"))
        repo.update_status(entry1["id"], MergeQueueStatus.MERGING.value)
        repo.update_status(entry1["id"], MergeQueueStatus.MERGED.value)

        # Now entry2 should be able to become merging.
        assert repo.update_status(entry2["id"], MergeQueueStatus.MERGING.value)

    def test_update_status_returns_false_for_missing_entry(
        self, repo: SQLiteMergeQueueRepository
    ):
        assert repo.update_status("nonexistent", MergeQueueStatus.MERGING.value) is False

    def test_update_to_merged_sets_merged_at(self, repo: SQLiteMergeQueueRepository):
        entry = repo.enqueue(_make_entry(task_id="task-1"))
        repo.update_status(entry["id"], MergeQueueStatus.MERGED.value)
        fetched = repo.get_by_id(entry["id"])
        assert fetched is not None
        assert fetched["merged_at"] is not None

    def test_update_to_non_merging_status_always_allowed(
        self, repo: SQLiteMergeQueueRepository
    ):
        entry1 = repo.enqueue(_make_entry(task_id="task-1"))
        entry2 = repo.enqueue(_make_entry(task_id="task-2"))
        repo.update_status(entry1["id"], MergeQueueStatus.MERGING.value)

        # Should be fine to set entry2 to a non-merging status.
        assert repo.update_status(entry2["id"], MergeQueueStatus.REBASING.value)


# ------------------------------------------------------------------
# TT-110-03: list_by_conversation returns entries ordered by
#             position ascending
# ------------------------------------------------------------------


class TestListByConversation:
    def test_returns_entries_ordered_by_position(
        self, repo: SQLiteMergeQueueRepository
    ):
        repo.enqueue(_make_entry(task_id="task-1"))
        repo.enqueue(_make_entry(task_id="task-2"))
        repo.enqueue(_make_entry(task_id="task-3"))

        entries = repo.list_by_conversation("conv-1")
        assert len(entries) == 3
        positions = [e["position"] for e in entries]
        assert positions == [1, 2, 3]

    def test_order_preserved_after_reorder(self, repo: SQLiteMergeQueueRepository):
        e1 = repo.enqueue(_make_entry(task_id="task-1"))
        e2 = repo.enqueue(_make_entry(task_id="task-2"))
        e3 = repo.enqueue(_make_entry(task_id="task-3"))

        # Reverse the order.
        repo.reorder("conv-1", [e3["id"], e2["id"], e1["id"]])

        entries = repo.list_by_conversation("conv-1")
        ids = [e["id"] for e in entries]
        assert ids == [e3["id"], e2["id"], e1["id"]]
        positions = [e["position"] for e in entries]
        assert positions == [1, 2, 3]

    def test_returns_empty_for_unknown_conversation(
        self, repo: SQLiteMergeQueueRepository
    ):
        assert repo.list_by_conversation("nonexistent") == []


# ------------------------------------------------------------------
# TT-110-04: assign_reviewer updates the reviewer_agent_id field
# ------------------------------------------------------------------


class TestAssignReviewer:
    def test_assigns_reviewer(self, repo: SQLiteMergeQueueRepository):
        entry = repo.enqueue(_make_entry(task_id="task-1"))
        assert entry.get("reviewer_agent_id") is None

        result = repo.assign_reviewer(entry["id"], "agent-2")
        assert result is True

        fetched = repo.get_by_id(entry["id"])
        assert fetched is not None
        assert fetched["reviewer_agent_id"] == "agent-2"

    def test_assign_reviewer_returns_false_for_missing(
        self, repo: SQLiteMergeQueueRepository
    ):
        assert repo.assign_reviewer("nonexistent", "agent-2") is False


# ------------------------------------------------------------------
# Additional: get_by_id, get_current_merging
# ------------------------------------------------------------------


class TestGetById:
    def test_returns_none_for_missing(self, repo: SQLiteMergeQueueRepository):
        assert repo.get_by_id("nonexistent") is None


class TestGetCurrentMerging:
    def test_returns_none_when_nothing_merging(
        self, repo: SQLiteMergeQueueRepository
    ):
        repo.enqueue(_make_entry(task_id="task-1"))
        assert repo.get_current_merging("conv-1") is None

    def test_returns_merging_entry(self, repo: SQLiteMergeQueueRepository):
        entry = repo.enqueue(_make_entry(task_id="task-1"))
        repo.update_status(entry["id"], MergeQueueStatus.MERGING.value)

        merging = repo.get_current_merging("conv-1")
        assert merging is not None
        assert merging["id"] == entry["id"]
        assert merging["status"] == MergeQueueStatus.MERGING.value

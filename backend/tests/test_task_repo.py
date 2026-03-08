"""Tests for SQLiteTaskRepository (T-107).

TDD test cases verifying CRUD operations and dependency-gate logic.
"""

from __future__ import annotations

import json

import pytest

from agent_orchestrator.orchestrator.models import Task, TaskStatus
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_task import SQLiteTaskRepository


@pytest.fixture
def repo():
    """Create an in-memory DB with schema and return a SQLiteTaskRepository."""
    db = DatabaseManager(":memory:")
    db.initialize()
    yield SQLiteTaskRepository(db)
    db.close()


@pytest.fixture
def db_and_repo():
    """Return both the DatabaseManager and repo for tests that need direct DB access."""
    db = DatabaseManager(":memory:")
    db.initialize()
    yield db, SQLiteTaskRepository(db)
    db.close()


# ------------------------------------------------------------------
# TT-107-01: create returns Task with default status 'todo'
# ------------------------------------------------------------------


class TestCreate:
    def test_returns_task_with_todo_status(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Build widget", '{"desc": "build it"}')
        assert isinstance(task, Task)
        assert task.status == TaskStatus.TODO
        assert task.conversation_id == "conv-1"
        assert task.title == "Build widget"

    def test_generates_uuid_id(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}")
        assert len(task.id) == 36  # UUID format

    def test_default_priority(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}")
        assert task.priority == 100

    def test_custom_priority(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}", priority=10)
        assert task.priority == 10

    def test_depends_on_stored_as_json(self, repo: SQLiteTaskRepository):
        dep_ids = ["dep-1", "dep-2"]
        task = repo.create("conv-1", "Task A", "{}", depends_on=dep_ids)
        assert json.loads(task.depends_on_json) == dep_ids

    def test_persisted_and_retrievable(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", '{"x": 1}')
        fetched = repo.get_by_id(task.id)
        assert fetched is not None
        assert fetched.id == task.id
        assert fetched.title == "Task A"
        assert fetched.status == TaskStatus.TODO


# ------------------------------------------------------------------
# TT-107-02: update_status to 'in_progress' blocked when deps not done
# ------------------------------------------------------------------


class TestDependencyGateBlocked:
    def test_blocked_when_dep_is_todo(self, repo: SQLiteTaskRepository):
        dep = repo.create("conv-1", "Dep task", "{}")
        task = repo.create("conv-1", "Main task", "{}", depends_on=[dep.id])

        with pytest.raises(ValueError, match="dependency.*status.*todo"):
            repo.update_status(task.id, TaskStatus.IN_PROGRESS)

    def test_blocked_when_dep_is_in_progress(self, repo: SQLiteTaskRepository):
        dep = repo.create("conv-1", "Dep task", "{}")
        repo.update_status(dep.id, TaskStatus.IN_PROGRESS)
        task = repo.create("conv-1", "Main task", "{}", depends_on=[dep.id])

        with pytest.raises(ValueError, match="dependency"):
            repo.update_status(task.id, TaskStatus.IN_PROGRESS)

    def test_blocked_when_one_of_multiple_deps_not_done(
        self, repo: SQLiteTaskRepository
    ):
        dep_a = repo.create("conv-1", "Dep A", "{}")
        dep_b = repo.create("conv-1", "Dep B", "{}")
        repo.update_status(dep_a.id, TaskStatus.DONE)
        # dep_b still 'todo'
        task = repo.create(
            "conv-1", "Main task", "{}", depends_on=[dep_a.id, dep_b.id]
        )

        with pytest.raises(ValueError, match="dependency"):
            repo.update_status(task.id, TaskStatus.IN_PROGRESS)

    def test_blocked_when_dep_does_not_exist(self, repo: SQLiteTaskRepository):
        task = repo.create(
            "conv-1", "Main task", "{}", depends_on=["nonexistent-id"]
        )

        with pytest.raises(ValueError, match="dependency"):
            repo.update_status(task.id, TaskStatus.IN_PROGRESS)


# ------------------------------------------------------------------
# TT-107-03: update_status to 'in_progress' succeeds when deps done
# ------------------------------------------------------------------


class TestDependencyGateSuccess:
    def test_succeeds_when_all_deps_done(self, repo: SQLiteTaskRepository):
        dep_a = repo.create("conv-1", "Dep A", "{}")
        dep_b = repo.create("conv-1", "Dep B", "{}")
        repo.update_status(dep_a.id, TaskStatus.DONE)
        repo.update_status(dep_b.id, TaskStatus.DONE)

        task = repo.create(
            "conv-1", "Main task", "{}", depends_on=[dep_a.id, dep_b.id]
        )
        repo.update_status(task.id, TaskStatus.IN_PROGRESS)

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.IN_PROGRESS

    def test_succeeds_with_no_deps(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "No deps", "{}")
        repo.update_status(task.id, TaskStatus.IN_PROGRESS)

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.IN_PROGRESS

    def test_sets_started_at_on_in_progress(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}")
        repo.update_status(task.id, TaskStatus.IN_PROGRESS)

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.started_at is not None

    def test_sets_finished_at_on_done(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}")
        repo.update_status(task.id, TaskStatus.DONE)

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.finished_at is not None


# ------------------------------------------------------------------
# TT-107-04: list_by_conversation with status_filter
# ------------------------------------------------------------------


class TestListByConversation:
    def test_returns_all_tasks_for_conversation(self, repo: SQLiteTaskRepository):
        repo.create("conv-1", "Task A", "{}")
        repo.create("conv-1", "Task B", "{}")
        repo.create("conv-2", "Task C", "{}")  # different conversation

        tasks = repo.list_by_conversation("conv-1")
        assert len(tasks) == 2
        assert all(t.conversation_id == "conv-1" for t in tasks)

    def test_status_filter_returns_matching_only(self, repo: SQLiteTaskRepository):
        task_a = repo.create("conv-1", "Task A", "{}")
        repo.create("conv-1", "Task B", "{}")
        repo.update_status(task_a.id, TaskStatus.DONE)

        done_tasks = repo.list_by_conversation(
            "conv-1", status_filter=TaskStatus.DONE
        )
        assert len(done_tasks) == 1
        assert done_tasks[0].status == TaskStatus.DONE

        todo_tasks = repo.list_by_conversation(
            "conv-1", status_filter=TaskStatus.TODO
        )
        assert len(todo_tasks) == 1
        assert todo_tasks[0].status == TaskStatus.TODO

    def test_returns_empty_for_no_match(self, repo: SQLiteTaskRepository):
        repo.create("conv-1", "Task A", "{}")
        tasks = repo.list_by_conversation(
            "conv-1", status_filter=TaskStatus.FAILED
        )
        assert tasks == []

    def test_returns_empty_for_unknown_conversation(
        self, repo: SQLiteTaskRepository
    ):
        tasks = repo.list_by_conversation("nonexistent")
        assert tasks == []


# ------------------------------------------------------------------
# Additional: get_by_id, assign_owner, update_result
# ------------------------------------------------------------------


class TestGetById:
    def test_returns_none_for_missing(self, repo: SQLiteTaskRepository):
        assert repo.get_by_id("nonexistent") is None


class TestAssignOwner:
    def test_sets_owner_agent_id(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}")
        repo.assign_owner(task.id, "agent-42")

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.owner_agent_id == "agent-42"

    def test_raises_for_missing_task(self, repo: SQLiteTaskRepository):
        with pytest.raises(KeyError):
            repo.assign_owner("nonexistent", "agent-42")


class TestUpdateResult:
    def test_sets_result_and_evidence(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Task A", "{}")
        repo.update_result(task.id, "All tests pass", '[{"file": "test.py"}]')

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.result_summary == "All tests pass"
        assert json.loads(updated.evidence_json) == [{"file": "test.py"}]

    def test_raises_for_missing_task(self, repo: SQLiteTaskRepository):
        with pytest.raises(KeyError):
            repo.update_result("nonexistent", "summary", "[]")


class TestUpdateStatusEdgeCases:
    def test_raises_key_error_for_missing_task(self, repo: SQLiteTaskRepository):
        with pytest.raises(KeyError):
            repo.update_status("nonexistent", TaskStatus.DONE)

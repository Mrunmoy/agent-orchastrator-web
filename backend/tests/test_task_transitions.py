"""Tests for TaskStatus state-machine enforcement in SQLiteTaskRepository (T-205).

Verifies that update_status() enforces VALID_TRANSITIONS from models.py.
"""

from __future__ import annotations

import pytest

from agent_orchestrator.orchestrator.models import VALID_TRANSITIONS, TaskStatus
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_task import SQLiteTaskRepository

_NOW = "2026-03-07T00:00:00Z"

# The happy-path sequence through all phases to DONE.
_FULL_LIFECYCLE: list[TaskStatus] = [
    TaskStatus.TODO,
    TaskStatus.DESIGN,
    TaskStatus.TDD,
    TaskStatus.IMPLEMENTING,
    TaskStatus.TESTING,
    TaskStatus.PR_RAISED,
    TaskStatus.IN_REVIEW,
    TaskStatus.MERGING,
    TaskStatus.DONE,
]


def _seed_conversations(db: DatabaseManager) -> None:
    with db.connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO conversation" " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "conv-1",
                "Conv",
                "/tmp",
                "debate",
                "design_debate",
                "open",
                100,
                1,
                None,
                None,
                _NOW,
                _NOW,
                None,
            ),
        )
        conn.commit()


@pytest.fixture
def repo():
    db = DatabaseManager(":memory:")
    db.initialize()
    _seed_conversations(db)
    yield SQLiteTaskRepository(db)
    db.close()


def _advance_to(repo: SQLiteTaskRepository, task_id: str, target: TaskStatus) -> None:
    """Walk a task from TODO through the happy path up to *target*."""
    for status in _FULL_LIFECYCLE[1:]:  # skip TODO (initial state)
        repo.update_status(task_id, status)
        if status == target:
            return
    raise ValueError(f"Target {target} not in happy-path lifecycle")


# ------------------------------------------------------------------
# TT-205-01: Valid forward transitions succeed
# ------------------------------------------------------------------


class TestValidForwardTransitions:
    def test_full_lifecycle_succeeds(self, repo: SQLiteTaskRepository):
        """Walk a task through the entire happy path TODO -> ... -> DONE."""
        task = repo.create("conv-1", "Lifecycle task", "{}")
        for status in _FULL_LIFECYCLE[1:]:
            repo.update_status(task.id, status)

        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.DONE

    def test_each_valid_transition(self, repo: SQLiteTaskRepository):
        """Every transition listed in VALID_TRANSITIONS should succeed."""
        for from_status, valid_targets in VALID_TRANSITIONS.items():
            for to_status in valid_targets:
                task = repo.create("conv-1", f"{from_status.value}->{to_status.value}", "{}")
                # Bring task to from_status first
                if from_status != TaskStatus.TODO:
                    if from_status == TaskStatus.BLOCKED:
                        repo.update_status(task.id, TaskStatus.BLOCKED)
                    elif from_status == TaskStatus.FIXING_COMMENTS:
                        # Need to reach FIXING_COMMENTS via IN_REVIEW
                        _advance_to(repo, task.id, TaskStatus.IN_REVIEW)
                        repo.update_status(task.id, TaskStatus.FIXING_COMMENTS)
                    else:
                        _advance_to(repo, task.id, from_status)

                # Now apply the transition under test
                repo.update_status(task.id, to_status)
                updated = repo.get_by_id(task.id)
                assert updated is not None
                assert updated.status == to_status, (
                    f"Expected {to_status} after {from_status} -> {to_status}, "
                    f"got {updated.status}"
                )

    def test_in_review_to_fixing_comments(self, repo: SQLiteTaskRepository):
        """IN_REVIEW -> FIXING_COMMENTS is valid."""
        task = repo.create("conv-1", "Review task", "{}")
        _advance_to(repo, task.id, TaskStatus.IN_REVIEW)
        repo.update_status(task.id, TaskStatus.FIXING_COMMENTS)
        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.FIXING_COMMENTS

    def test_fixing_comments_to_in_review(self, repo: SQLiteTaskRepository):
        """FIXING_COMMENTS -> IN_REVIEW (cycle back) is valid."""
        task = repo.create("conv-1", "Fix cycle task", "{}")
        _advance_to(repo, task.id, TaskStatus.IN_REVIEW)
        repo.update_status(task.id, TaskStatus.FIXING_COMMENTS)
        repo.update_status(task.id, TaskStatus.IN_REVIEW)
        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.IN_REVIEW


# ------------------------------------------------------------------
# TT-205-02: Invalid transitions raise ValueError
# ------------------------------------------------------------------


class TestInvalidTransitions:
    def test_todo_to_implementing_raises(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Skip task", "{}")
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.IMPLEMENTING)

    def test_todo_to_done_raises(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Shortcut task", "{}")
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.DONE)

    def test_todo_to_testing_raises(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Skip task", "{}")
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.TESTING)

    def test_design_to_implementing_raises(self, repo: SQLiteTaskRepository):
        """DESIGN must go through TDD first."""
        task = repo.create("conv-1", "Skip TDD", "{}")
        repo.update_status(task.id, TaskStatus.DESIGN)
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.IMPLEMENTING)

    def test_implementing_to_done_raises(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Skip review", "{}")
        _advance_to(repo, task.id, TaskStatus.IMPLEMENTING)
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.DONE)

    def test_merging_to_todo_raises(self, repo: SQLiteTaskRepository):
        task = repo.create("conv-1", "Backward", "{}")
        _advance_to(repo, task.id, TaskStatus.MERGING)
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.TODO)


# ------------------------------------------------------------------
# TT-205-03: Any status can transition to BLOCKED
# ------------------------------------------------------------------


class TestTransitionToBlocked:
    @pytest.mark.parametrize(
        "target_status",
        [s for s in TaskStatus if s not in (TaskStatus.DONE, TaskStatus.BLOCKED)],
    )
    def test_any_active_status_to_blocked(
        self, repo: SQLiteTaskRepository, target_status: TaskStatus
    ):
        task = repo.create("conv-1", f"Block from {target_status.value}", "{}")
        if target_status == TaskStatus.FIXING_COMMENTS:
            _advance_to(repo, task.id, TaskStatus.IN_REVIEW)
            repo.update_status(task.id, TaskStatus.FIXING_COMMENTS)
        elif target_status != TaskStatus.TODO:
            _advance_to(repo, task.id, target_status)
        repo.update_status(task.id, TaskStatus.BLOCKED)
        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == TaskStatus.BLOCKED


# ------------------------------------------------------------------
# TT-205-04: BLOCKED can go back to any non-terminal status
# ------------------------------------------------------------------


class TestBlockedTransitions:
    @pytest.mark.parametrize(
        "target_status",
        [s for s in TaskStatus if s not in (TaskStatus.DONE, TaskStatus.BLOCKED)],
    )
    def test_blocked_to_any_non_terminal(
        self, repo: SQLiteTaskRepository, target_status: TaskStatus
    ):
        task = repo.create("conv-1", f"Unblock to {target_status.value}", "{}")
        repo.update_status(task.id, TaskStatus.BLOCKED)
        repo.update_status(task.id, target_status)
        updated = repo.get_by_id(task.id)
        assert updated is not None
        assert updated.status == target_status

    def test_blocked_to_done_raises(self, repo: SQLiteTaskRepository):
        """BLOCKED cannot go directly to DONE (terminal)."""
        task = repo.create("conv-1", "Blocked done", "{}")
        repo.update_status(task.id, TaskStatus.BLOCKED)
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, TaskStatus.DONE)


# ------------------------------------------------------------------
# TT-205-05: DONE is terminal
# ------------------------------------------------------------------


class TestDoneIsTerminal:
    @pytest.mark.parametrize("target_status", list(TaskStatus))
    def test_done_to_anything_raises(self, repo: SQLiteTaskRepository, target_status: TaskStatus):
        """DONE is terminal — cannot transition to any status."""
        task = repo.create("conv-1", "Done task", "{}")
        _advance_to(repo, task.id, TaskStatus.DONE)
        # Even transitioning DONE -> DONE should fail (empty valid set)
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.update_status(task.id, target_status)

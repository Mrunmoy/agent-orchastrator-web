"""Tests for the merge coordinator queue model (COORD-001)."""

from __future__ import annotations

import pytest

from agent_orchestrator.orchestrator.merge_queue import (
    MergeCoordinator,
    MergeRequest,
    MergeStatus,
)


class TestMergeStatus:
    def test_enum_values(self) -> None:
        assert MergeStatus.PENDING == "pending"
        assert MergeStatus.IN_PROGRESS == "in_progress"
        assert MergeStatus.MERGED == "merged"
        assert MergeStatus.FAILED == "failed"
        assert MergeStatus.CANCELLED == "cancelled"


class TestMergeRequest:
    def test_defaults(self) -> None:
        req = MergeRequest(
            task_id="T-1",
            branch_name="feature/foo",
            requested_at="2026-03-07T00:00:00Z",
        )
        assert req.status == MergeStatus.PENDING
        assert req.started_at is None
        assert req.completed_at is None
        assert req.error_message is None


class TestMergeCoordinator:
    def setup_method(self) -> None:
        self.coord = MergeCoordinator()

    # --- submit ---

    def test_submit_adds_to_queue(self) -> None:
        req = self.coord.submit("T-1", "feature/foo")
        assert req.task_id == "T-1"
        assert req.branch_name == "feature/foo"
        assert req.status == MergeStatus.PENDING
        assert req.requested_at  # non-empty ISO timestamp

    def test_submit_duplicate_raises(self) -> None:
        self.coord.submit("T-1", "feature/foo")
        with pytest.raises(ValueError, match="T-1"):
            self.coord.submit("T-1", "feature/bar")

    # --- next ---

    def test_next_returns_fifo_order(self) -> None:
        self.coord.submit("T-1", "branch-1")
        self.coord.submit("T-2", "branch-2")
        first = self.coord.next()
        assert first is not None
        assert first.task_id == "T-1"
        # Must complete T-1 before T-2 can be advanced
        self.coord.complete("T-1")
        second = self.coord.next()
        assert second is not None
        assert second.task_id == "T-2"

    def test_next_returns_active_if_in_progress(self) -> None:
        self.coord.submit("T-1", "branch-1")
        self.coord.submit("T-2", "branch-2")
        first = self.coord.next()
        assert first is not None
        assert first.task_id == "T-1"
        # Calling next() again should return the same active request, not T-2
        second = self.coord.next()
        assert second is not None
        assert second.task_id == "T-1"
        assert second.status == MergeStatus.IN_PROGRESS

    def test_next_returns_none_when_empty(self) -> None:
        assert self.coord.next() is None

    def test_next_marks_in_progress_with_started_at(self) -> None:
        self.coord.submit("T-1", "branch-1")
        req = self.coord.next()
        assert req is not None
        assert req.status == MergeStatus.IN_PROGRESS
        assert req.started_at is not None

    # --- complete ---

    def test_complete_marks_merged(self) -> None:
        self.coord.submit("T-1", "branch-1")
        self.coord.next()
        req = self.coord.complete("T-1")
        assert req.status == MergeStatus.MERGED
        assert req.completed_at is not None

    def test_complete_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            self.coord.complete("no-such-task")

    # --- fail ---

    def test_fail_marks_failed_with_error(self) -> None:
        self.coord.submit("T-1", "branch-1")
        self.coord.next()
        req = self.coord.fail("T-1", "merge conflict")
        assert req.status == MergeStatus.FAILED
        assert req.error_message == "merge conflict"
        assert req.completed_at is not None

    def test_fail_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            self.coord.fail("no-such-task", "err")

    # --- cancel ---

    def test_cancel_marks_cancelled(self) -> None:
        self.coord.submit("T-1", "branch-1")
        req = self.coord.cancel("T-1")
        assert req.status == MergeStatus.CANCELLED
        assert req.completed_at is not None

    def test_cancel_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            self.coord.cancel("no-such-task")

    # --- position ---

    def test_position_tracking(self) -> None:
        self.coord.submit("T-1", "b1")
        self.coord.submit("T-2", "b2")
        self.coord.submit("T-3", "b3")
        assert self.coord.position("T-1") == 0
        assert self.coord.position("T-2") == 1
        assert self.coord.position("T-3") == 2
        # After next(), T-1 is no longer pending
        self.coord.next()
        assert self.coord.position("T-1") is None
        assert self.coord.position("T-2") == 0

    def test_position_unknown_returns_none(self) -> None:
        assert self.coord.position("no-such-task") is None

    # --- pending ---

    def test_pending_filters_correctly(self) -> None:
        self.coord.submit("T-1", "b1")
        self.coord.submit("T-2", "b2")
        self.coord.next()  # T-1 becomes IN_PROGRESS
        pending = self.coord.pending()
        assert len(pending) == 1
        assert pending[0].task_id == "T-2"

    # --- history ---

    def test_history_returns_all(self) -> None:
        self.coord.submit("T-1", "b1")
        self.coord.submit("T-2", "b2")
        self.coord.next()
        self.coord.complete("T-1")
        history = self.coord.history()
        assert len(history) == 2
        task_ids = {r.task_id for r in history}
        assert task_ids == {"T-1", "T-2"}

    # --- active ---

    def test_active_returns_in_progress(self) -> None:
        self.coord.submit("T-1", "b1")
        assert self.coord.active() is None
        self.coord.next()
        active = self.coord.active()
        assert active is not None
        assert active.task_id == "T-1"
        assert active.status == MergeStatus.IN_PROGRESS

    def test_active_returns_none_after_complete(self) -> None:
        self.coord.submit("T-1", "b1")
        self.coord.next()
        self.coord.complete("T-1")
        assert self.coord.active() is None

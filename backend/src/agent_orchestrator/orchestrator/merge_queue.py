"""Merge coordinator queue model (COORD-001).

Ensures branches are integrated one at a time in FIFO order to avoid conflicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class MergeStatus(str, Enum):
    """Status of a merge request in the queue."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    MERGED = "merged"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MergeRequest:
    """A request to merge a task branch into the main branch."""

    task_id: str
    branch_name: str
    status: MergeStatus = MergeStatus.PENDING
    requested_at: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MergeCoordinator:
    """FIFO queue that serialises branch merges one at a time."""

    def __init__(self) -> None:
        self._requests: list[MergeRequest] = []
        self._index: dict[str, MergeRequest] = {}

    def submit(self, task_id: str, branch_name: str) -> MergeRequest:
        """Add a merge request to the queue. Raises ValueError on duplicate."""
        if task_id in self._index:
            raise ValueError(f"Duplicate task_id: {task_id}")
        req = MergeRequest(
            task_id=task_id,
            branch_name=branch_name,
            requested_at=_now_iso(),
        )
        self._requests.append(req)
        self._index[task_id] = req
        return req

    def next(self) -> MergeRequest | None:
        """Get the next PENDING request (FIFO) and mark it IN_PROGRESS."""
        for req in self._requests:
            if req.status == MergeStatus.PENDING:
                req.status = MergeStatus.IN_PROGRESS
                req.started_at = _now_iso()
                return req
        return None

    def _lookup(self, task_id: str) -> MergeRequest:
        if task_id not in self._index:
            raise ValueError(f"unknown task_id: {task_id}")
        return self._index[task_id]

    def complete(self, task_id: str) -> MergeRequest:
        """Mark a request as MERGED."""
        req = self._lookup(task_id)
        req.status = MergeStatus.MERGED
        req.completed_at = _now_iso()
        return req

    def fail(self, task_id: str, error: str) -> MergeRequest:
        """Mark a request as FAILED with an error message."""
        req = self._lookup(task_id)
        req.status = MergeStatus.FAILED
        req.error_message = error
        req.completed_at = _now_iso()
        return req

    def cancel(self, task_id: str) -> MergeRequest:
        """Mark a request as CANCELLED."""
        req = self._lookup(task_id)
        req.status = MergeStatus.CANCELLED
        req.completed_at = _now_iso()
        return req

    def position(self, task_id: str) -> int | None:
        """Return 0-indexed position among PENDING items, or None."""
        idx = 0
        for req in self._requests:
            if req.status == MergeStatus.PENDING:
                if req.task_id == task_id:
                    return idx
                idx += 1
        return None

    def pending(self) -> list[MergeRequest]:
        """Return all PENDING requests in queue order."""
        return [r for r in self._requests if r.status == MergeStatus.PENDING]

    def history(self) -> list[MergeRequest]:
        """Return all requests regardless of status."""
        return list(self._requests)

    def active(self) -> MergeRequest | None:
        """Return the IN_PROGRESS request, if any."""
        for req in self._requests:
            if req.status == MergeStatus.IN_PROGRESS:
                return req
        return None

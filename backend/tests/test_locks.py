"""Tests for branch/task lock policy (COORD-002)."""

from __future__ import annotations

import time
from datetime import datetime

import pytest

from agent_orchestrator.orchestrator.locks import (
    Lock,
    LockConflictError,
    LockManager,
    LockType,
)


class TestLockType:
    def test_enum_values(self):
        assert LockType.BRANCH == "branch"
        assert LockType.FILE == "file"
        assert LockType.TASK == "task"

    def test_is_str(self):
        assert isinstance(LockType.BRANCH, str)


class TestLockConflictError:
    def test_attributes(self):
        err = LockConflictError(resource="main", owner="agent-2", existing_owner="agent-1")
        assert err.resource == "main"
        assert err.owner == "agent-2"
        assert err.existing_owner == "agent-1"

    def test_is_exception(self):
        assert issubclass(LockConflictError, Exception)


class TestLockManagerAcquire:
    def test_acquire_creates_lock(self):
        mgr = LockManager()
        lock = mgr.acquire(LockType.BRANCH, "main", "agent-1")
        assert isinstance(lock, Lock)
        assert lock.lock_type == LockType.BRANCH
        assert lock.resource == "main"
        assert lock.owner == "agent-1"
        assert lock.acquired_at is not None
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(lock.acquired_at)
        assert lock.expires_at is None

    def test_acquire_same_owner_is_idempotent(self):
        mgr = LockManager()
        lock1 = mgr.acquire(LockType.BRANCH, "main", "agent-1")
        lock2 = mgr.acquire(LockType.BRANCH, "main", "agent-1")
        assert lock1 is lock2

    def test_acquire_different_owner_raises_conflict(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        with pytest.raises(LockConflictError) as exc_info:
            mgr.acquire(LockType.BRANCH, "main", "agent-2")
        assert exc_info.value.resource == "main"
        assert exc_info.value.owner == "agent-2"
        assert exc_info.value.existing_owner == "agent-1"

    def test_acquire_with_ttl_sets_expires_at(self):
        mgr = LockManager()
        lock = mgr.acquire(LockType.FILE, "src/app.py", "agent-1", ttl_seconds=60)
        assert lock.expires_at is not None
        expires = datetime.fromisoformat(lock.expires_at)
        acquired = datetime.fromisoformat(lock.acquired_at)
        diff = (expires - acquired).total_seconds()
        assert 59 <= diff <= 61


class TestLockManagerRelease:
    def test_release_by_owner_succeeds(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        assert mgr.release(LockType.BRANCH, "main", "agent-1") is True
        assert mgr.is_locked("main") is False

    def test_release_by_non_owner_fails(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        assert mgr.release(LockType.BRANCH, "main", "agent-2") is False
        assert mgr.is_locked("main") is True

    def test_release_unknown_resource_returns_false(self):
        mgr = LockManager()
        assert mgr.release(LockType.BRANCH, "nonexistent", "agent-1") is False

    def test_release_only_affects_matching_lock_type(self):
        """Releasing a BRANCH lock must not affect a FILE lock on same resource."""
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        mgr.acquire(LockType.FILE, "main", "agent-2")
        assert mgr.release(LockType.BRANCH, "main", "agent-1") is True
        # FILE lock on "main" should still be active
        file_lock = mgr.get_lock("main")
        assert file_lock is not None
        assert file_lock.lock_type == LockType.FILE
        assert file_lock.owner == "agent-2"


class TestLockManagerIsLocked:
    def test_is_locked_returns_correct_state(self):
        mgr = LockManager()
        assert mgr.is_locked("main") is False
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        assert mgr.is_locked("main") is True
        mgr.release(LockType.BRANCH, "main", "agent-1")
        assert mgr.is_locked("main") is False


class TestLockManagerGetLock:
    def test_get_lock_returns_none_for_expired(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1", ttl_seconds=0)
        # Sleep briefly to ensure expiry
        time.sleep(0.01)
        assert mgr.get_lock("main") is None

    def test_get_lock_returns_lock_when_active(self):
        mgr = LockManager()
        lock = mgr.acquire(LockType.BRANCH, "main", "agent-1")
        assert mgr.get_lock("main") is lock

    def test_get_lock_returns_none_for_unknown(self):
        mgr = LockManager()
        assert mgr.get_lock("nonexistent") is None


class TestLockManagerLocksByOwner:
    def test_locks_by_owner_filters_correctly(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        mgr.acquire(LockType.FILE, "src/app.py", "agent-1")
        mgr.acquire(LockType.TASK, "TASK-001", "agent-2")

        agent1_locks = mgr.locks_by_owner("agent-1")
        assert len(agent1_locks) == 2
        resources = {lock.resource for lock in agent1_locks}
        assert resources == {"main", "src/app.py"}

        agent2_locks = mgr.locks_by_owner("agent-2")
        assert len(agent2_locks) == 1
        assert agent2_locks[0].resource == "TASK-001"

    def test_locks_by_owner_excludes_expired(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1", ttl_seconds=0)
        mgr.acquire(LockType.FILE, "src/app.py", "agent-1")
        time.sleep(0.01)
        locks = mgr.locks_by_owner("agent-1")
        assert len(locks) == 1
        assert locks[0].resource == "src/app.py"


class TestLockManagerReleaseAll:
    def test_release_all_clears_owner_locks(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1")
        mgr.acquire(LockType.FILE, "src/app.py", "agent-1")
        mgr.acquire(LockType.TASK, "TASK-001", "agent-2")

        count = mgr.release_all("agent-1")
        assert count == 2
        assert mgr.is_locked("main") is False
        assert mgr.is_locked("src/app.py") is False
        assert mgr.is_locked("TASK-001") is True


class TestLockManagerCleanupExpired:
    def test_cleanup_expired_removes_stale_locks(self):
        mgr = LockManager()
        mgr.acquire(LockType.BRANCH, "main", "agent-1", ttl_seconds=0)
        mgr.acquire(LockType.FILE, "src/app.py", "agent-1")
        time.sleep(0.01)

        count = mgr.cleanup_expired()
        assert count == 1
        assert mgr.get_lock("main") is None
        assert mgr.get_lock("src/app.py") is not None


class TestLockTypesIndependent:
    def test_different_lock_types_on_same_resource_name_are_independent(self):
        """Different lock types on the same resource name should not conflict."""
        mgr = LockManager()
        lock_branch = mgr.acquire(LockType.BRANCH, "main", "agent-1")
        lock_file = mgr.acquire(LockType.FILE, "main", "agent-2")
        lock_task = mgr.acquire(LockType.TASK, "main", "agent-3")

        assert lock_branch.owner == "agent-1"
        assert lock_file.owner == "agent-2"
        assert lock_task.owner == "agent-3"

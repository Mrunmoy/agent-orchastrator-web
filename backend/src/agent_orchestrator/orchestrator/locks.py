"""Branch/task lock policy to avoid multi-agent file conflicts (COORD-002)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum


class LockType(str, Enum):
    BRANCH = "branch"
    FILE = "file"
    TASK = "task"


@dataclass
class Lock:
    lock_type: LockType
    resource: str
    owner: str
    acquired_at: str
    expires_at: str | None = None


class LockConflictError(Exception):
    """Raised when a lock is already held by a different owner."""

    def __init__(self, resource: str, owner: str, existing_owner: str) -> None:
        self.resource = resource
        self.owner = owner
        self.existing_owner = existing_owner
        super().__init__(
            f"Resource {resource!r} is locked by {existing_owner!r}, "
            f"cannot acquire for {owner!r}"
        )


def _make_key(lock_type: LockType, resource: str) -> tuple[str, str]:
    return (lock_type.value, resource)


class LockManager:
    """In-memory lock manager for coordinating agent access to resources."""

    def __init__(self) -> None:
        self._locks: dict[tuple[str, str], Lock] = {}

    def _is_expired(self, lock: Lock) -> bool:
        if lock.expires_at is None:
            return False
        return datetime.now(timezone.utc) >= datetime.fromisoformat(lock.expires_at)

    def acquire(
        self,
        lock_type: LockType,
        resource: str,
        owner: str,
        ttl_seconds: int | None = None,
    ) -> Lock:
        key = _make_key(lock_type, resource)
        existing = self._locks.get(key)

        if existing is not None and not self._is_expired(existing):
            if existing.owner == owner:
                return existing
            raise LockConflictError(
                resource=resource, owner=owner, existing_owner=existing.owner
            )

        now = datetime.now(timezone.utc)
        expires_at: str | None = None
        if ttl_seconds is not None:
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()

        lock = Lock(
            lock_type=lock_type,
            resource=resource,
            owner=owner,
            acquired_at=now.isoformat(),
            expires_at=expires_at,
        )
        self._locks[key] = lock
        return lock

    def release(self, lock_type: LockType, resource: str, owner: str) -> bool:
        """Release a lock. Only the owner can release. Returns True if released."""
        key = _make_key(lock_type, resource)
        existing = self._locks.get(key)
        if existing is None:
            return False
        if existing.owner != owner:
            return False
        del self._locks[key]
        return True

    def is_locked(self, resource: str) -> bool:
        for key, lock in self._locks.items():
            if key[1] == resource and not self._is_expired(lock):
                return True
        return False

    def get_lock(self, resource: str) -> Lock | None:
        for key, lock in list(self._locks.items()):
            if key[1] == resource:
                if self._is_expired(lock):
                    return None
                return lock
        return None

    def locks_by_owner(self, owner: str) -> list[Lock]:
        return [
            lock
            for lock in self._locks.values()
            if lock.owner == owner and not self._is_expired(lock)
        ]

    def release_all(self, owner: str) -> int:
        to_remove = [key for key, lock in self._locks.items() if lock.owner == owner]
        for key in to_remove:
            del self._locks[key]
        return len(to_remove)

    def cleanup_expired(self) -> int:
        to_remove = [key for key, lock in self._locks.items() if self._is_expired(lock)]
        for key in to_remove:
            del self._locks[key]
        return len(to_remove)

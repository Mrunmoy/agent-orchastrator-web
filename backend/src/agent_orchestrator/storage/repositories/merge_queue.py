"""MergeQueueRepository ABC (T-103).

No domain model exists yet for merge-queue entries, so methods use
``dict[str, Any]`` until a ``MergeEntry`` dataclass is added.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from agent_orchestrator.storage.repositories.base import BaseRepository


class MergeQueueRepository(BaseRepository):
    """Abstract interface for merge-queue persistence."""

    @abstractmethod
    def enqueue(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Add a new entry to the merge queue and return it."""
        ...

    @abstractmethod
    def get_by_id(self, entry_id: str) -> dict[str, Any] | None:
        """Return the queue entry with the given ID, or ``None``."""
        ...

    @abstractmethod
    def list_by_conversation(self, conversation_id: str) -> list[dict[str, Any]]:
        """Return all queue entries for a conversation, in queue order."""
        ...

    @abstractmethod
    def update_status(self, entry_id: str, status: str) -> bool:
        """Update the status of a queue entry. Return ``True`` on success."""
        ...

    @abstractmethod
    def assign_reviewer(self, entry_id: str, reviewer_agent_id: str) -> bool:
        """Assign a reviewer agent to a queue entry. Return ``True`` on success."""
        ...

    @abstractmethod
    def reorder(self, conversation_id: str, ordered_ids: list[str]) -> bool:
        """Reorder queue entries for a conversation. Return ``True`` on success."""
        ...

    @abstractmethod
    def get_current_merging(self, conversation_id: str) -> dict[str, Any] | None:
        """Return the entry currently being merged, or ``None``."""
        ...

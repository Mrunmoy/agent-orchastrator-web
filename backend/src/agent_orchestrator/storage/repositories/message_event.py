"""MessageEventRepository ABC (T-103).

Append-only: no update or delete operations.
"""

from __future__ import annotations

from abc import abstractmethod

from agent_orchestrator.orchestrator.models import MessageEvent
from agent_orchestrator.storage.repositories.base import BaseRepository


class MessageEventRepository(BaseRepository):
    """Abstract interface for MessageEvent persistence (append-only)."""

    @abstractmethod
    def append(self, event: MessageEvent) -> MessageEvent:
        """Append a new event and return it (with assigned ID if applicable)."""
        ...

    @abstractmethod
    def get_by_event_id(self, event_id: str) -> MessageEvent | None:
        """Return the event with the given event_id, or ``None``."""
        ...

    @abstractmethod
    def list_by_conversation(
        self, conversation_id: str, *, limit: int = 100, offset: int = 0
    ) -> list[MessageEvent]:
        """Return events for a conversation with pagination."""
        ...

    @abstractmethod
    def list_by_type(self, conversation_id: str, event_type: str) -> list[MessageEvent]:
        """Return events of a specific type within a conversation."""
        ...

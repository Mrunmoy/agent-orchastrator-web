"""ConversationRepository ABC (T-103)."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from agent_orchestrator.orchestrator.models import Conversation
from agent_orchestrator.storage.repositories.base import BaseRepository


class ConversationRepository(BaseRepository):
    """Abstract interface for Conversation persistence."""

    @abstractmethod
    def create(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation and return the stored entity."""
        ...

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> Conversation | None:
        """Return the conversation with the given ID, or ``None``."""
        ...

    @abstractmethod
    def list_active(self) -> list[Conversation]:
        """Return all non-deleted conversations ordered by updated_at DESC."""
        ...

    @abstractmethod
    def update(self, conversation_id: str, fields: dict[str, Any]) -> Conversation | None:
        """Partially update a conversation. Return the updated entity or ``None``."""
        ...

    @abstractmethod
    def soft_delete(self, conversation_id: str) -> bool:
        """Mark a conversation as deleted. Return ``True`` on success."""
        ...

    @abstractmethod
    def clear_all(self) -> int:
        """Soft-delete all non-deleted conversations. Return count deleted."""
        ...

    @abstractmethod
    def select(self, conversation_id: str) -> Conversation | None:
        """Set one conversation as active, deactivating all others. Return it."""
        ...

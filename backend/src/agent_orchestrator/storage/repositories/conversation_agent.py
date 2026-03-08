"""ConversationAgentRepository ABC (T-106).

Defines the contract for managing the conversation_agent join table,
including agent assignment, reordering, and merge coordinator designation.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from agent_orchestrator.storage.repositories.base import BaseRepository


class ConversationAgentRepository(BaseRepository):
    """Abstract interface for conversation-agent join persistence."""

    @abstractmethod
    def add_agent_to_conversation(
        self,
        conversation_id: str,
        agent_id: str,
        permission_profile: str = "default",
    ) -> dict[str, Any]:
        """Add an agent to a conversation.

        Auto-assigns ``turn_order`` as max(existing) + 1, starting from 1.
        Returns the created join record as a dict.
        """
        ...

    @abstractmethod
    def remove_agent(self, conversation_id: str, agent_id: str) -> None:
        """Remove an agent from a conversation (deletes the join row)."""
        ...

    @abstractmethod
    def list_agents(self, conversation_id: str) -> list[dict[str, Any]]:
        """Return agents for a conversation, ordered by turn_order."""
        ...

    @abstractmethod
    def reorder(self, conversation_id: str, agent_ids: list[str]) -> None:
        """Reorder agents atomically.  ``agent_ids`` specifies the desired order (1-based)."""
        ...

    @abstractmethod
    def set_merge_coordinator(self, conversation_id: str, agent_id: str) -> None:
        """Clear existing merge coordinator(s) and set a new one."""
        ...

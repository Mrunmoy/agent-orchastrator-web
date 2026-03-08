"""AgentRepository ABC (T-103)."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from agent_orchestrator.orchestrator.models import Agent
from agent_orchestrator.storage.repositories.base import BaseRepository


class AgentRepository(BaseRepository):
    """Abstract interface for Agent persistence."""

    @abstractmethod
    def create(self, agent: Agent) -> Agent:
        """Persist a new agent and return the stored entity."""
        ...

    @abstractmethod
    def get_by_id(self, agent_id: str) -> Agent | None:
        """Return the agent with the given ID, or ``None``."""
        ...

    @abstractmethod
    def list_all(self) -> list[Agent]:
        """Return all agents ordered by sort_order."""
        ...

    @abstractmethod
    def update(self, agent_id: str, fields: dict[str, Any]) -> Agent | None:
        """Partially update an agent. Return the updated entity or ``None``."""
        ...

    @abstractmethod
    def delete(self, agent_id: str) -> bool:
        """Delete an agent. Return ``True`` on success."""
        ...

    @abstractmethod
    def update_sort_order(self, agent_id: str, sort_order: int) -> bool:
        """Update the display sort order for an agent. Return ``True`` on success."""
        ...

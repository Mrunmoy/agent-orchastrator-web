"""TaskRepository ABC (T-103)."""

from __future__ import annotations

from abc import abstractmethod

from agent_orchestrator.orchestrator.models import Task, TaskStatus
from agent_orchestrator.storage.repositories.base import BaseRepository


class TaskRepository(BaseRepository):
    """Abstract interface for Task persistence."""

    @abstractmethod
    def create(self, task: Task) -> Task:
        """Persist a new task and return the stored entity."""
        ...

    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None:
        """Return the task with the given ID, or ``None``."""
        ...

    @abstractmethod
    def list_by_conversation(self, conversation_id: str) -> list[Task]:
        """Return all tasks for a conversation, ordered by priority."""
        ...

    @abstractmethod
    def update_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a task. Return ``True`` on success."""
        ...

    @abstractmethod
    def assign_owner(self, task_id: str, agent_id: str) -> bool:
        """Assign an agent as owner of a task. Return ``True`` on success."""
        ...

    @abstractmethod
    def update_result(self, task_id: str, result_summary: str, evidence_json: str) -> bool:
        """Record the result of a completed task. Return ``True`` on success."""
        ...

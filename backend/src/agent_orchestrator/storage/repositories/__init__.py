"""Repository abstract interfaces for the storage layer (T-103).

Each ABC defines the contract for a single entity's persistence operations.
Concrete implementations (SQLite, in-memory, etc.) will live alongside.
"""

from agent_orchestrator.storage.repositories.agent import AgentRepository
from agent_orchestrator.storage.repositories.artifact import ArtifactRepository
from agent_orchestrator.storage.repositories.base import BaseRepository
from agent_orchestrator.storage.repositories.conversation import ConversationRepository
from agent_orchestrator.storage.repositories.merge_queue import MergeQueueRepository
from agent_orchestrator.storage.repositories.message_event import MessageEventRepository
from agent_orchestrator.storage.repositories.task import TaskRepository

__all__ = [
    "BaseRepository",
    "ConversationRepository",
    "AgentRepository",
    "TaskRepository",
    "MessageEventRepository",
    "ArtifactRepository",
    "MergeQueueRepository",
]

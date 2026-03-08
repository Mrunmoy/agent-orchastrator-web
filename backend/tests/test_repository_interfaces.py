"""Tests for storage repository abstract interfaces (T-103).

TT-103-01: ABCs cannot be instantiated directly.
TT-103-02: ABCs define required CRUD method signatures with correct type hints.
TT-103-03: Minimal concrete subclass can be created by implementing all methods.
"""

from __future__ import annotations

import inspect
from typing import Any, get_type_hints

import pytest

from agent_orchestrator.orchestrator.models import (
    Agent,
    Artifact,
    Conversation,
    MessageEvent,
    Task,
    TaskStatus,
)
from agent_orchestrator.storage.repositories import (
    AgentRepository,
    ArtifactRepository,
    ConversationRepository,
    MergeQueueRepository,
    MessageEventRepository,
    TaskRepository,
)


# -----------------------------------------------------------------------
# TT-103-01: ABCs cannot be instantiated directly
# -----------------------------------------------------------------------


class TestABCsCannotBeInstantiated:
    """All repository ABCs must raise TypeError on direct instantiation."""

    @pytest.mark.parametrize(
        "abc_cls",
        [
            ConversationRepository,
            AgentRepository,
            TaskRepository,
            MessageEventRepository,
            ArtifactRepository,
            MergeQueueRepository,
        ],
    )
    def test_cannot_instantiate(self, abc_cls: type) -> None:
        with pytest.raises(TypeError):
            abc_cls()  # type: ignore[abstract]


# -----------------------------------------------------------------------
# TT-103-02: ABCs define required method signatures
# -----------------------------------------------------------------------


class TestConversationRepositorySignatures:
    REQUIRED_METHODS = [
        "create",
        "get_by_id",
        "list_active",
        "update",
        "soft_delete",
        "clear_all",
        "select",
    ]

    def test_has_all_methods(self) -> None:
        for name in self.REQUIRED_METHODS:
            assert hasattr(ConversationRepository, name), f"Missing method: {name}"
            assert callable(getattr(ConversationRepository, name))

    def test_create_signature(self) -> None:
        hints = get_type_hints(ConversationRepository.create)
        assert "conversation" in hints
        assert hints["conversation"] is Conversation
        assert hints["return"] is Conversation

    def test_get_by_id_signature(self) -> None:
        hints = get_type_hints(ConversationRepository.get_by_id)
        assert "conversation_id" in hints
        assert hints["conversation_id"] is str
        # Return is Optional[Conversation]
        assert hints["return"] is Conversation or "Conversation" in str(hints["return"])

    def test_list_active_returns_list(self) -> None:
        hints = get_type_hints(ConversationRepository.list_active)
        ret = str(hints["return"])
        assert "list" in ret.lower()

    def test_update_signature(self) -> None:
        hints = get_type_hints(ConversationRepository.update)
        assert "conversation_id" in hints
        assert "fields" in hints

    def test_soft_delete_signature(self) -> None:
        hints = get_type_hints(ConversationRepository.soft_delete)
        assert "conversation_id" in hints

    def test_clear_all_signature(self) -> None:
        hints = get_type_hints(ConversationRepository.clear_all)
        assert hints["return"] is int

    def test_select_signature(self) -> None:
        hints = get_type_hints(ConversationRepository.select)
        assert "conversation_id" in hints


class TestAgentRepositorySignatures:
    REQUIRED_METHODS = [
        "create",
        "get_by_id",
        "list_all",
        "update",
        "delete",
        "update_sort_order",
    ]

    def test_has_all_methods(self) -> None:
        for name in self.REQUIRED_METHODS:
            assert hasattr(AgentRepository, name), f"Missing method: {name}"

    def test_create_returns_agent(self) -> None:
        hints = get_type_hints(AgentRepository.create)
        assert hints["return"] is Agent

    def test_update_sort_order_signature(self) -> None:
        hints = get_type_hints(AgentRepository.update_sort_order)
        assert "agent_id" in hints
        assert "sort_order" in hints


class TestTaskRepositorySignatures:
    REQUIRED_METHODS = [
        "create",
        "get_by_id",
        "list_by_conversation",
        "update_status",
        "assign_owner",
        "update_result",
    ]

    def test_has_all_methods(self) -> None:
        for name in self.REQUIRED_METHODS:
            assert hasattr(TaskRepository, name), f"Missing method: {name}"

    def test_update_status_signature(self) -> None:
        hints = get_type_hints(TaskRepository.update_status)
        assert "task_id" in hints
        assert "status" in hints
        assert hints["status"] is TaskStatus

    def test_assign_owner_signature(self) -> None:
        hints = get_type_hints(TaskRepository.assign_owner)
        assert "task_id" in hints
        assert "agent_id" in hints

    def test_list_by_conversation_signature(self) -> None:
        hints = get_type_hints(TaskRepository.list_by_conversation)
        assert "conversation_id" in hints


class TestMessageEventRepositorySignatures:
    REQUIRED_METHODS = [
        "append",
        "get_by_event_id",
        "list_by_conversation",
        "list_by_type",
    ]

    def test_has_all_methods(self) -> None:
        for name in self.REQUIRED_METHODS:
            assert hasattr(MessageEventRepository, name), f"Missing method: {name}"

    def test_no_update_or_delete(self) -> None:
        """MessageEvent is append-only — no update or delete methods."""
        assert not hasattr(MessageEventRepository, "update")
        assert not hasattr(MessageEventRepository, "delete")

    def test_append_signature(self) -> None:
        hints = get_type_hints(MessageEventRepository.append)
        assert "event" in hints
        assert hints["event"] is MessageEvent

    def test_list_by_type_signature(self) -> None:
        hints = get_type_hints(MessageEventRepository.list_by_type)
        assert "conversation_id" in hints
        assert "event_type" in hints


class TestArtifactRepositorySignatures:
    REQUIRED_METHODS = ["create", "get_by_id", "list_by_conversation", "get_latest"]

    def test_has_all_methods(self) -> None:
        for name in self.REQUIRED_METHODS:
            assert hasattr(ArtifactRepository, name), f"Missing method: {name}"

    def test_get_latest_signature(self) -> None:
        hints = get_type_hints(ArtifactRepository.get_latest)
        assert "conversation_id" in hints


class TestMergeQueueRepositorySignatures:
    REQUIRED_METHODS = [
        "enqueue",
        "get_by_id",
        "list_by_conversation",
        "update_status",
        "assign_reviewer",
        "reorder",
        "get_current_merging",
    ]

    def test_has_all_methods(self) -> None:
        for name in self.REQUIRED_METHODS:
            assert hasattr(MergeQueueRepository, name), f"Missing method: {name}"

    def test_assign_reviewer_signature(self) -> None:
        hints = get_type_hints(MergeQueueRepository.assign_reviewer)
        assert "entry_id" in hints
        assert "reviewer_agent_id" in hints

    def test_get_current_merging_signature(self) -> None:
        hints = get_type_hints(MergeQueueRepository.get_current_merging)
        assert "conversation_id" in hints


# -----------------------------------------------------------------------
# TT-103-03: Minimal concrete subclass can be created
# -----------------------------------------------------------------------


class TestConcreteSubclasses:
    """A concrete subclass implementing all abstract methods can be instantiated."""

    def test_concrete_conversation_repo(self) -> None:
        class InMemory(ConversationRepository):
            def create(self, conversation: Conversation) -> Conversation:
                return conversation

            def get_by_id(self, conversation_id: str) -> Conversation | None:
                return None

            def list_active(self) -> list[Conversation]:
                return []

            def update(
                self, conversation_id: str, fields: dict[str, Any]
            ) -> Conversation | None:
                return None

            def soft_delete(self, conversation_id: str) -> bool:
                return False

            def clear_all(self) -> int:
                return 0

            def select(self, conversation_id: str) -> Conversation | None:
                return None

        repo = InMemory()
        assert repo.list_active() == []

    def test_concrete_agent_repo(self) -> None:
        class InMemory(AgentRepository):
            def create(self, agent: Agent) -> Agent:
                return agent

            def get_by_id(self, agent_id: str) -> Agent | None:
                return None

            def list_all(self) -> list[Agent]:
                return []

            def update(self, agent_id: str, fields: dict[str, Any]) -> Agent | None:
                return None

            def delete(self, agent_id: str) -> bool:
                return False

            def update_sort_order(self, agent_id: str, sort_order: int) -> bool:
                return False

        repo = InMemory()
        assert repo.list_all() == []

    def test_concrete_task_repo(self) -> None:
        class InMemory(TaskRepository):
            def create(self, task: Task) -> Task:
                return task

            def get_by_id(self, task_id: str) -> Task | None:
                return None

            def list_by_conversation(self, conversation_id: str) -> list[Task]:
                return []

            def update_status(self, task_id: str, status: TaskStatus) -> bool:
                return False

            def assign_owner(self, task_id: str, agent_id: str) -> bool:
                return False

            def update_result(
                self, task_id: str, result_summary: str, evidence_json: str
            ) -> bool:
                return False

        repo = InMemory()
        assert repo.list_by_conversation("x") == []

    def test_concrete_message_event_repo(self) -> None:
        class InMemory(MessageEventRepository):
            def append(self, event: MessageEvent) -> MessageEvent:
                return event

            def get_by_event_id(self, event_id: str) -> MessageEvent | None:
                return None

            def list_by_conversation(
                self, conversation_id: str, *, limit: int = 100, offset: int = 0
            ) -> list[MessageEvent]:
                return []

            def list_by_type(
                self, conversation_id: str, event_type: str
            ) -> list[MessageEvent]:
                return []

        repo = InMemory()
        assert repo.list_by_conversation("x") == []

    def test_concrete_artifact_repo(self) -> None:
        class InMemory(ArtifactRepository):
            def create(self, artifact: Artifact) -> Artifact:
                return artifact

            def get_by_id(self, artifact_id: str) -> Artifact | None:
                return None

            def list_by_conversation(self, conversation_id: str) -> list[Artifact]:
                return []

            def get_latest(self, conversation_id: str) -> Artifact | None:
                return None

        repo = InMemory()
        assert repo.list_by_conversation("x") == []

    def test_concrete_merge_queue_repo(self) -> None:
        class InMemory(MergeQueueRepository):
            def enqueue(self, entry: dict[str, Any]) -> dict[str, Any]:
                return entry

            def get_by_id(self, entry_id: str) -> dict[str, Any] | None:
                return None

            def list_by_conversation(
                self, conversation_id: str
            ) -> list[dict[str, Any]]:
                return []

            def update_status(self, entry_id: str, status: str) -> bool:
                return False

            def assign_reviewer(
                self, entry_id: str, reviewer_agent_id: str
            ) -> bool:
                return False

            def reorder(
                self, conversation_id: str, ordered_ids: list[str]
            ) -> bool:
                return False

            def get_current_merging(
                self, conversation_id: str
            ) -> dict[str, Any] | None:
                return None

        repo = InMemory()
        assert repo.list_by_conversation("x") == []

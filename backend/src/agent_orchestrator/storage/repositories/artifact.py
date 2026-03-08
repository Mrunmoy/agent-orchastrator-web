"""ArtifactRepository ABC (T-103)."""

from __future__ import annotations

from abc import abstractmethod

from agent_orchestrator.orchestrator.models import Artifact, ArtifactType
from agent_orchestrator.storage.repositories.base import BaseRepository


class ArtifactRepository(BaseRepository):
    """Abstract interface for Artifact persistence."""

    @abstractmethod
    def create(self, artifact: Artifact) -> Artifact:
        """Persist a new artifact and return the stored entity."""
        ...

    @abstractmethod
    def get_by_id(self, artifact_id: str) -> Artifact | None:
        """Return the artifact with the given ID, or ``None``."""
        ...

    @abstractmethod
    def list_by_conversation(
        self, conversation_id: str, *, type_filter: ArtifactType | None = None
    ) -> list[Artifact]:
        """Return all artifacts for a conversation, ordered by created_at DESC.

        If *type_filter* is given, only artifacts of that type are returned.
        """
        ...

    @abstractmethod
    def get_latest(self, conversation_id: str) -> Artifact | None:
        """Return the most recent artifact for a conversation, or ``None``."""
        ...

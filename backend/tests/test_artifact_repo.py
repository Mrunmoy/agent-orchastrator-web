"""Tests for SQLiteArtifactRepository (T-109).

TDD test suite covering create, get_by_id, list_by_conversation (with
type_filter), and get_latest.
"""

from __future__ import annotations

import time

import pytest

from agent_orchestrator.orchestrator.models import Artifact, ArtifactType
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_artifact import (
    SQLiteArtifactRepository,
)


_NOW = "2026-03-07T00:00:00Z"


def _seed_conversations(db: DatabaseManager) -> None:
    """Insert conversation rows referenced by FK constraints."""
    with db.connection() as conn:
        for cid in ("conv-1", "conv-2", "conv-abc"):
            conn.execute(
                "INSERT OR IGNORE INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, "Conv", "/tmp", "debate", "design_debate", "open", 100, 1, None, None, _NOW, _NOW, None),
            )
        conn.commit()


@pytest.fixture()
def repo() -> SQLiteArtifactRepository:
    """Return a repository backed by a fresh in-memory database."""
    db = DatabaseManager(":memory:")
    db.initialize()
    _seed_conversations(db)
    return SQLiteArtifactRepository(db)


def _make_artifact(
    conversation_id: str = "conv-1",
    artifact_type: ArtifactType = ArtifactType.AGREEMENT_MAP,
    payload: str = '{"key": "value"}',
    batch_id: str | None = None,
) -> Artifact:
    """Build an Artifact suitable for passing to repo.create."""
    return Artifact(
        id="",
        conversation_id=conversation_id,
        type=artifact_type,
        payload_json=payload,
        created_at="",
        batch_id=batch_id,
    )


# ── TT-109-01: create returns Artifact with generated UUID and correct type ──


class TestCreate:
    def test_returns_artifact_with_uuid(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact())
        assert len(art.id) == 36  # UUID format

    def test_correct_type(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact(artifact_type=ArtifactType.CHECKPOINT))
        assert art.type == ArtifactType.CHECKPOINT

    def test_conversation_id_preserved(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact(conversation_id="conv-abc"))
        assert art.conversation_id == "conv-abc"

    def test_payload_json_preserved(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact(payload='{"x": 1}'))
        assert art.payload_json == '{"x": 1}'

    def test_batch_id_stored(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact(batch_id="batch-42"))
        assert art.batch_id == "batch-42"

    def test_batch_id_none_by_default(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact())
        assert art.batch_id is None

    def test_created_at_set(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact())
        assert art.created_at is not None
        assert art.created_at != ""

    def test_get_by_id_returns_created(self, repo: SQLiteArtifactRepository):
        art = repo.create(_make_artifact())
        fetched = repo.get_by_id(art.id)
        assert fetched is not None
        assert fetched.id == art.id

    def test_get_by_id_returns_none_for_missing(self, repo: SQLiteArtifactRepository):
        assert repo.get_by_id("nonexistent") is None


# ── TT-109-02: list_by_conversation with type_filter returns only matching ────


class TestListByConversation:
    def test_returns_all_for_conversation(self, repo: SQLiteArtifactRepository):
        repo.create(_make_artifact(artifact_type=ArtifactType.AGREEMENT_MAP))
        repo.create(_make_artifact(artifact_type=ArtifactType.CHECKPOINT))
        results = repo.list_by_conversation("conv-1")
        assert len(results) == 2

    def test_type_filter_returns_only_matching(self, repo: SQLiteArtifactRepository):
        repo.create(_make_artifact(artifact_type=ArtifactType.AGREEMENT_MAP))
        repo.create(_make_artifact(artifact_type=ArtifactType.CHECKPOINT))
        repo.create(_make_artifact(artifact_type=ArtifactType.AGREEMENT_MAP))
        results = repo.list_by_conversation(
            "conv-1", type_filter=ArtifactType.AGREEMENT_MAP
        )
        assert len(results) == 2
        assert all(a.type == ArtifactType.AGREEMENT_MAP for a in results)

    def test_type_filter_no_match(self, repo: SQLiteArtifactRepository):
        repo.create(_make_artifact(artifact_type=ArtifactType.AGREEMENT_MAP))
        results = repo.list_by_conversation(
            "conv-1", type_filter=ArtifactType.TEST_REPORT
        )
        assert results == []

    def test_excludes_other_conversations(self, repo: SQLiteArtifactRepository):
        repo.create(_make_artifact(conversation_id="conv-1"))
        repo.create(_make_artifact(conversation_id="conv-2"))
        results = repo.list_by_conversation("conv-1")
        assert len(results) == 1
        assert results[0].conversation_id == "conv-1"

    def test_ordered_by_created_at_desc(self, repo: SQLiteArtifactRepository):
        a1 = repo.create(_make_artifact())
        # Small delay to ensure different timestamps
        time.sleep(0.01)
        a2 = repo.create(_make_artifact())
        results = repo.list_by_conversation("conv-1")
        assert results[0].id == a2.id
        assert results[1].id == a1.id

    def test_empty_for_unknown_conversation(self, repo: SQLiteArtifactRepository):
        assert repo.list_by_conversation("nonexistent") == []


# ── TT-109-03: get_latest returns most recently created artifact ──────────────


class TestGetLatest:
    def test_returns_most_recent(self, repo: SQLiteArtifactRepository):
        repo.create(_make_artifact(artifact_type=ArtifactType.AGREEMENT_MAP))
        time.sleep(0.01)
        second = repo.create(_make_artifact(artifact_type=ArtifactType.CHECKPOINT))
        latest = repo.get_latest("conv-1")
        assert latest is not None
        assert latest.id == second.id

    def test_returns_none_when_empty(self, repo: SQLiteArtifactRepository):
        assert repo.get_latest("conv-1") is None

    def test_scoped_to_conversation(self, repo: SQLiteArtifactRepository):
        repo.create(_make_artifact(conversation_id="conv-1"))
        time.sleep(0.01)
        repo.create(_make_artifact(conversation_id="conv-2"))
        latest = repo.get_latest("conv-1")
        assert latest is not None
        assert latest.conversation_id == "conv-1"

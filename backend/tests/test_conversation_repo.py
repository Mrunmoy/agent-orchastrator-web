"""Tests for SQLiteConversationRepository (T-104).

TDD test suite covering create, soft_delete, select, clear_all, update,
get_by_id, and list_active.
"""

from __future__ import annotations

import pytest

from agent_orchestrator.orchestrator.models import ConversationState, GateStatus, Phase
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_conversation import (
    SQLiteConversationRepository,
)


@pytest.fixture()
def repo() -> SQLiteConversationRepository:
    """Return a repository backed by a fresh in-memory database."""
    db = DatabaseManager(":memory:")
    db.initialize()
    return SQLiteConversationRepository(db)


# ── TT-104-01: create returns Conversation with generated UUID and defaults ──


class TestCreate:
    def test_returns_conversation_with_uuid(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp/project")
        assert len(conv.id) == 36  # UUID format

    def test_title_and_project_path(self, repo: SQLiteConversationRepository):
        conv = repo.create("My Conv", "/home/user/proj")
        assert conv.title == "My Conv"
        assert conv.project_path == "/home/user/proj"

    def test_default_state(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        assert conv.state == ConversationState.DEBATE

    def test_default_phase(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        assert conv.phase == Phase.DESIGN_DEBATE

    def test_default_gate_status(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        assert conv.gate_status == GateStatus.OPEN

    def test_default_priority(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        assert conv.priority == 100

    def test_default_inactive(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        assert conv.active == 0

    def test_timestamps_set(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        assert conv.created_at is not None
        assert conv.updated_at is not None
        assert conv.deleted_at is None

    def test_get_by_id_returns_created(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        fetched = repo.get_by_id(conv.id)
        assert fetched is not None
        assert fetched.id == conv.id
        assert fetched.title == "Test"

    def test_get_by_id_returns_none_for_missing(self, repo: SQLiteConversationRepository):
        assert repo.get_by_id("nonexistent") is None


# ── TT-104-02: soft_delete sets deleted_at, list_active excludes it ──────────


class TestSoftDelete:
    def test_sets_deleted_at(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        deleted = repo.soft_delete(conv.id)
        assert deleted is not None
        assert deleted.deleted_at is not None

    def test_list_active_excludes_deleted(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        repo.soft_delete(conv.id)
        assert repo.list_active() == []

    def test_returns_none_for_missing(self, repo: SQLiteConversationRepository):
        assert repo.soft_delete("nonexistent") is None

    def test_returns_none_for_already_deleted(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        repo.soft_delete(conv.id)
        assert repo.soft_delete(conv.id) is None

    def test_list_active_returns_non_deleted(self, repo: SQLiteConversationRepository):
        c1 = repo.create("Keep", "/tmp")
        c2 = repo.create("Delete", "/tmp")
        repo.soft_delete(c2.id)
        active = repo.list_active()
        assert len(active) == 1
        assert active[0].id == c1.id


# ── TT-104-03: select atomically deactivates all, activates target ───────────


class TestSelect:
    def test_activates_target(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        selected = repo.select(conv.id)
        assert selected is not None
        assert selected.active == 1

    def test_deactivates_others(self, repo: SQLiteConversationRepository):
        c1 = repo.create("A", "/tmp")
        c2 = repo.create("B", "/tmp")
        repo.select(c1.id)
        repo.select(c2.id)
        # c1 should now be inactive, c2 active
        fetched_c1 = repo.get_by_id(c1.id)
        fetched_c2 = repo.get_by_id(c2.id)
        assert fetched_c1 is not None
        assert fetched_c1.active == 0
        assert fetched_c2 is not None
        assert fetched_c2.active == 1

    def test_returns_none_for_missing(self, repo: SQLiteConversationRepository):
        assert repo.select("nonexistent") is None

    def test_returns_none_for_deleted(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        repo.soft_delete(conv.id)
        assert repo.select(conv.id) is None

    def test_updates_selected_updated_at(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        original_updated = conv.updated_at
        selected = repo.select(conv.id)
        assert selected is not None
        # updated_at should be >= original (may be same if fast)
        assert selected.updated_at >= original_updated


# ── TT-104-04: clear_all soft-deletes all and returns count ──────────────────


class TestClearAll:
    def test_returns_count(self, repo: SQLiteConversationRepository):
        repo.create("A", "/tmp")
        repo.create("B", "/tmp")
        count = repo.clear_all()
        assert count == 2

    def test_conversations_excluded_from_list_active(self, repo: SQLiteConversationRepository):
        repo.create("A", "/tmp")
        repo.create("B", "/tmp")
        repo.clear_all()
        assert repo.list_active() == []

    def test_zero_when_none_exist(self, repo: SQLiteConversationRepository):
        assert repo.clear_all() == 0

    def test_does_not_redelete_already_deleted(self, repo: SQLiteConversationRepository):
        conv = repo.create("A", "/tmp")
        repo.soft_delete(conv.id)
        assert repo.clear_all() == 0


# ── update tests ─────────────────────────────────────────────────────────────


class TestUpdate:
    def test_partial_update_title(self, repo: SQLiteConversationRepository):
        conv = repo.create("Old", "/tmp")
        updated = repo.update(conv.id, {"title": "New"})
        assert updated.title == "New"

    def test_raises_for_missing(self, repo: SQLiteConversationRepository):
        with pytest.raises(ValueError, match="not found"):
            repo.update("nonexistent", {"title": "X"})

    def test_bumps_updated_at(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        original = conv.updated_at
        updated = repo.update(conv.id, {"title": "Changed"})
        assert updated.updated_at >= original

    def test_empty_fields_no_op(self, repo: SQLiteConversationRepository):
        conv = repo.create("Test", "/tmp")
        result = repo.update(conv.id, {})
        assert result.title == "Test"

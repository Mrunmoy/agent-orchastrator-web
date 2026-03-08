"""Tests for SQLiteConversationAgentRepository (T-106).

TDD tests covering add, remove, list, reorder, and merge coordinator
operations on the conversation_agent join table.
"""

from __future__ import annotations

import sqlite3
import uuid

import pytest

from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_conversation_agent import (
    SQLiteConversationAgentRepository,
)


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

NOW = "2026-03-08T00:00:00+00:00"


def _insert_conversation(conn, conv_id: str = "conv-1") -> str:
    """Insert a minimal conversation row and return its id."""
    conn.execute(
        "INSERT INTO conversation "
        "(id, title, project_path, state, phase, gate_status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (conv_id, "Test Conv", "/tmp", "debate", "design_debate", "open", NOW, NOW),
    )
    conn.commit()
    return conv_id


def _insert_agent(conn, agent_id: str | None = None, name: str = "Agent") -> str:
    """Insert a minimal agent row and return its id."""
    aid = agent_id or str(uuid.uuid4())
    conn.execute(
        "INSERT INTO agent "
        "(id, display_name, provider, model, personality_key, role, "
        " status, session_id, capabilities_json, sort_order, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (aid, name, "claude", "opus-4", None, "worker", "idle", None, "[]", 0, NOW, NOW),
    )
    conn.commit()
    return aid


@pytest.fixture
def setup():
    """Provide DB, repo, conversation id, and helper to create agents."""
    db = DatabaseManager(":memory:")
    db.initialize()
    repo = SQLiteConversationAgentRepository(db)

    with db.connection() as conn:
        conv_id = _insert_conversation(conn)

    def make_agent(name: str = "Agent", agent_id: str | None = None) -> str:
        with db.connection() as conn:
            return _insert_agent(conn, agent_id=agent_id, name=name)

    yield db, repo, conv_id, make_agent
    db.close()


# -----------------------------------------------------------------------
# TT-106-01: add_agent auto-assigns turn_order as max(existing)+1
# -----------------------------------------------------------------------


class TestAddAgent:
    def test_first_agent_gets_turn_order_1(self, setup):
        db, repo, conv_id, make_agent = setup
        agent_id = make_agent("First")

        result = repo.add_agent_to_conversation(conv_id, agent_id)

        assert result["conversation_id"] == conv_id
        assert result["agent_id"] == agent_id
        assert result["turn_order"] == 1
        assert result["permission_profile"] == "default"
        assert result["is_merge_coordinator"] == 0
        assert result["enabled"] == 1

    def test_second_agent_gets_turn_order_2(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("First")
        a2 = make_agent("Second")

        repo.add_agent_to_conversation(conv_id, a1)
        result = repo.add_agent_to_conversation(conv_id, a2)

        assert result["turn_order"] == 2

    def test_third_agent_gets_turn_order_3(self, setup):
        db, repo, conv_id, make_agent = setup
        agents = [make_agent(f"Agent-{i}") for i in range(3)]

        for a in agents:
            repo.add_agent_to_conversation(conv_id, a)

        listed = repo.list_agents(conv_id)
        assert [d["turn_order"] for d in listed] == [1, 2, 3]

    def test_custom_permission_profile(self, setup):
        db, repo, conv_id, make_agent = setup
        a = make_agent("Custom")

        result = repo.add_agent_to_conversation(conv_id, a, permission_profile="read_only")
        assert result["permission_profile"] == "read_only"


# -----------------------------------------------------------------------
# TT-106-02: Adding same agent twice raises IntegrityError
# -----------------------------------------------------------------------


class TestAddAgentDuplicate:
    def test_duplicate_raises_integrity_error(self, setup):
        db, repo, conv_id, make_agent = setup
        a = make_agent("Dup")

        repo.add_agent_to_conversation(conv_id, a)

        with pytest.raises(sqlite3.IntegrityError):
            repo.add_agent_to_conversation(conv_id, a)


# -----------------------------------------------------------------------
# TT-106-03: reorder updates turn_order atomically in specified order
# -----------------------------------------------------------------------


class TestReorder:
    def test_reorder_updates_turn_order(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("A")
        a2 = make_agent("B")
        a3 = make_agent("C")

        repo.add_agent_to_conversation(conv_id, a1)
        repo.add_agent_to_conversation(conv_id, a2)
        repo.add_agent_to_conversation(conv_id, a3)

        # Reverse the order
        repo.reorder(conv_id, [a3, a2, a1])

        listed = repo.list_agents(conv_id)
        assert [d["agent_id"] for d in listed] == [a3, a2, a1]
        assert [d["turn_order"] for d in listed] == [1, 2, 3]

    def test_reorder_mismatched_ids_raises(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("A")
        repo.add_agent_to_conversation(conv_id, a1)

        with pytest.raises(ValueError, match="must exactly match"):
            repo.reorder(conv_id, [a1, "nonexistent"])

    def test_reorder_missing_ids_raises(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("A")
        a2 = make_agent("B")
        repo.add_agent_to_conversation(conv_id, a1)
        repo.add_agent_to_conversation(conv_id, a2)

        # Only supply one of two
        with pytest.raises(ValueError, match="must exactly match"):
            repo.reorder(conv_id, [a1])


# -----------------------------------------------------------------------
# TT-106-04: set_merge_coordinator clears existing and sets new one
# -----------------------------------------------------------------------


class TestSetMergeCoordinator:
    def test_sets_merge_coordinator(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("A")
        a2 = make_agent("B")

        repo.add_agent_to_conversation(conv_id, a1)
        repo.add_agent_to_conversation(conv_id, a2)

        repo.set_merge_coordinator(conv_id, a1)

        listed = repo.list_agents(conv_id)
        mc = {d["agent_id"]: d["is_merge_coordinator"] for d in listed}
        assert mc[a1] == 1
        assert mc[a2] == 0

    def test_changing_coordinator_clears_previous(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("A")
        a2 = make_agent("B")

        repo.add_agent_to_conversation(conv_id, a1)
        repo.add_agent_to_conversation(conv_id, a2)

        repo.set_merge_coordinator(conv_id, a1)
        repo.set_merge_coordinator(conv_id, a2)

        listed = repo.list_agents(conv_id)
        mc = {d["agent_id"]: d["is_merge_coordinator"] for d in listed}
        assert mc[a1] == 0
        assert mc[a2] == 1

    def test_set_coordinator_on_unlinked_agent_raises(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("A")

        with pytest.raises(KeyError):
            repo.set_merge_coordinator(conv_id, a1)


# -----------------------------------------------------------------------
# Remove agent
# -----------------------------------------------------------------------


class TestRemoveAgent:
    def test_remove_agent(self, setup):
        db, repo, conv_id, make_agent = setup
        a = make_agent("A")
        repo.add_agent_to_conversation(conv_id, a)

        repo.remove_agent(conv_id, a)

        assert repo.list_agents(conv_id) == []

    def test_remove_unlinked_agent_raises(self, setup):
        db, repo, conv_id, make_agent = setup
        with pytest.raises(KeyError):
            repo.remove_agent(conv_id, "nonexistent")


# -----------------------------------------------------------------------
# List agents
# -----------------------------------------------------------------------


class TestListAgents:
    def test_empty_conversation_returns_empty_list(self, setup):
        db, repo, conv_id, make_agent = setup
        assert repo.list_agents(conv_id) == []

    def test_list_returns_ordered_by_turn_order(self, setup):
        db, repo, conv_id, make_agent = setup
        a1 = make_agent("Alpha")
        a2 = make_agent("Beta")

        repo.add_agent_to_conversation(conv_id, a2)
        repo.add_agent_to_conversation(conv_id, a1)

        listed = repo.list_agents(conv_id)
        assert listed[0]["agent_id"] == a2
        assert listed[1]["agent_id"] == a1

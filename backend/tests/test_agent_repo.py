"""Tests for SQLiteAgentRepository (T-105).

TDD tests covering CRUD operations, enum validation, ordering,
and cascade delete behaviour.
"""

from __future__ import annotations

import uuid

import pytest

from agent_orchestrator.orchestrator.models import AgentRole, AgentStatus, Provider
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_agent import SQLiteAgentRepository


@pytest.fixture
def repo():
    """Provide a SQLiteAgentRepository backed by an in-memory DB."""
    db = DatabaseManager(":memory:")
    db.initialize()
    yield SQLiteAgentRepository(db)
    db.close()


@pytest.fixture
def db_and_repo():
    """Provide both DatabaseManager and repo for join-table tests."""
    db = DatabaseManager(":memory:")
    db.initialize()
    yield db, SQLiteAgentRepository(db)
    db.close()


# -----------------------------------------------------------------------
# TT-105-01: create with valid provider/role returns Agent with UUID + idle
# -----------------------------------------------------------------------


class TestCreate:
    def test_create_returns_agent_with_uuid_and_idle_status(self, repo: SQLiteAgentRepository):
        agent = repo.create(
            display_name="Claude Worker",
            provider="claude",
            model="opus-4",
            role="worker",
        )

        # Valid UUID
        uuid.UUID(agent.id)  # raises if invalid

        assert agent.display_name == "Claude Worker"
        assert agent.provider == Provider.CLAUDE
        assert agent.model == "opus-4"
        assert agent.role == AgentRole.WORKER
        assert agent.status == AgentStatus.IDLE
        assert agent.personality_key is None
        assert agent.capabilities_json == "[]"
        assert agent.created_at  # non-empty
        assert agent.updated_at  # non-empty

    def test_create_with_personality_key(self, repo: SQLiteAgentRepository):
        agent = repo.create(
            display_name="Codex Planner",
            provider="codex",
            model="codex-1",
            role="coordinator",
            personality_key="careful_planner",
        )

        assert agent.personality_key == "careful_planner"
        assert agent.role == AgentRole.COORDINATOR

    def test_create_persists_to_db(self, repo: SQLiteAgentRepository):
        agent = repo.create(
            display_name="Persisted",
            provider="claude",
            model="opus-4",
            role="worker",
        )
        fetched = repo.get_by_id(agent.id)
        assert fetched is not None
        assert fetched.id == agent.id
        assert fetched.display_name == "Persisted"


# -----------------------------------------------------------------------
# TT-105-02: create with invalid provider raises ValueError
# -----------------------------------------------------------------------


class TestCreateValidation:
    def test_invalid_provider_raises(self, repo: SQLiteAgentRepository):
        with pytest.raises(ValueError, match="Invalid provider"):
            repo.create(
                display_name="Bad",
                provider="gpt5",
                model="x",
                role="worker",
            )

    def test_invalid_role_raises(self, repo: SQLiteAgentRepository):
        with pytest.raises(ValueError, match="Invalid role"):
            repo.create(
                display_name="Bad",
                provider="claude",
                model="x",
                role="overlord",
            )


# -----------------------------------------------------------------------
# TT-105-03: delete cascades to remove conversation_agent join rows
# -----------------------------------------------------------------------


class TestDeleteCascade:
    def test_delete_removes_agent(self, repo: SQLiteAgentRepository):
        agent = repo.create("Del", "claude", "opus-4", "worker")
        repo.delete(agent.id)
        assert repo.get_by_id(agent.id) is None

    def test_delete_nonexistent_raises(self, repo: SQLiteAgentRepository):
        with pytest.raises(KeyError):
            repo.delete("nonexistent-id")

    def test_delete_cascades_conversation_agent(self, db_and_repo):
        db, repo = db_and_repo
        agent = repo.create("CascadeTest", "claude", "opus-4", "worker")

        # Create a conversation so we can insert a join row
        with db.connection() as conn:
            now = "2026-03-08T00:00:00Z"
            conn.execute(
                "INSERT INTO conversation "
                "(id, title, project_path, state, phase, gate_status, "
                " created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("conv-1", "Test Conv", "/tmp", "debate", "design_debate", "open", now, now),
            )
            ca_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO conversation_agent "
                "(id, conversation_id, agent_id, turn_order, permission_profile, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ca_id, "conv-1", agent.id, 0, "default", now),
            )
            conn.commit()

            # Verify join row exists
            count = conn.execute(
                "SELECT COUNT(*) FROM conversation_agent WHERE agent_id = ?",
                (agent.id,),
            ).fetchone()[0]
            assert count == 1

        # Delete agent
        repo.delete(agent.id)

        # Verify join row is gone
        with db.connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM conversation_agent WHERE agent_id = ?",
                (agent.id,),
            ).fetchone()[0]
            assert count == 0


# -----------------------------------------------------------------------
# TT-105-04: list_all returns agents ordered by sort_order, then name
# -----------------------------------------------------------------------


class TestListAll:
    def test_list_all_ordered_by_sort_order_then_name(self, repo: SQLiteAgentRepository):
        # Create agents with different sort_orders and names
        a1 = repo.create("Zeta", "claude", "opus-4", "worker")
        a2 = repo.create("Alpha", "codex", "codex-1", "worker")
        a3 = repo.create("Beta", "claude", "opus-4", "coordinator")

        # Set sort_orders: Beta=0, Zeta=1, Alpha=1 (tie on sort_order)
        repo.update_sort_order(a3.id, 0)
        repo.update_sort_order(a1.id, 1)
        repo.update_sort_order(a2.id, 1)

        agents = repo.list_all()
        names = [a.display_name for a in agents]

        # Beta (sort_order=0) first, then Alpha and Zeta (sort_order=1, alpha order)
        assert names == ["Beta", "Alpha", "Zeta"]

    def test_list_all_empty(self, repo: SQLiteAgentRepository):
        assert repo.list_all() == []


# -----------------------------------------------------------------------
# Additional coverage: update, get_by_id, update_sort_order
# -----------------------------------------------------------------------


class TestUpdate:
    def test_update_partial_fields(self, repo: SQLiteAgentRepository):
        agent = repo.create("Original", "claude", "opus-4", "worker")
        updated = repo.update(agent.id, {"display_name": "Renamed"})
        assert updated.display_name == "Renamed"
        assert updated.provider == Provider.CLAUDE  # unchanged

    def test_update_nonexistent_raises(self, repo: SQLiteAgentRepository):
        with pytest.raises(KeyError):
            repo.update("no-such-id", {"display_name": "X"})

    def test_update_invalid_provider_raises(self, repo: SQLiteAgentRepository):
        agent = repo.create("A", "claude", "opus-4", "worker")
        with pytest.raises(ValueError, match="Invalid provider"):
            repo.update(agent.id, {"provider": "bad"})

    def test_update_invalid_role_raises(self, repo: SQLiteAgentRepository):
        agent = repo.create("A", "claude", "opus-4", "worker")
        with pytest.raises(ValueError, match="Invalid role"):
            repo.update(agent.id, {"role": "king"})


class TestGetById:
    def test_returns_none_for_missing(self, repo: SQLiteAgentRepository):
        assert repo.get_by_id("missing") is None


class TestUpdateSortOrder:
    def test_updates_sort_order(self, repo: SQLiteAgentRepository):
        agent = repo.create("A", "claude", "opus-4", "worker")
        repo.update_sort_order(agent.id, 5)
        fetched = repo.get_by_id(agent.id)
        assert fetched is not None
        # Verify via list_all ordering (sort_order is not on the Agent dataclass
        # but affects list_all ordering)
        agents = repo.list_all()
        assert agents[0].id == agent.id

    def test_nonexistent_raises(self, repo: SQLiteAgentRepository):
        with pytest.raises(KeyError):
            repo.update_sort_order("nope", 1)

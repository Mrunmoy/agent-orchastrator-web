"""Tests for conversation-scoped agent endpoints (UI-014)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agent_orchestrator.api import create_app
from agent_orchestrator.api.db_provider import _init_db


@pytest.fixture(autouse=True)
def _fresh_db():
    """Reset the in-memory database before each test."""
    _init_db()


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_conversation(client: TestClient, title: str = "Test Conv") -> str:
    """Create a conversation and return its id."""
    resp = client.post(
        "/api/conversations/new",
        json={
            "title": title,
            "project_path": "/tmp/test",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["conversation"]["id"]


def _create_agent(
    client: TestClient,
    name: str = "Agent A",
    *,
    conversation_id: str | None = None,
) -> dict:
    """Create an agent, optionally scoped to a conversation."""
    payload: dict = {
        "display_name": name,
        "provider": "claude",
        "model": "opus",
        "role": "worker",
    }
    if conversation_id is not None:
        payload["conversation_id"] = conversation_id
    resp = client.post("/api/agents", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["agent"]


# ── UI-014a: GET /conversations/{cid}/agents ──────────────────────


class TestListConversationAgents:
    def test_returns_empty_list_when_conversation_has_no_agents(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.get(f"/api/conversations/{cid}/agents")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["agents"] == []

    def test_returns_404_when_conversation_does_not_exist(self, client: TestClient):
        resp = client.get("/api/conversations/nonexistent/agents")
        assert resp.status_code == 404
        body = resp.json()
        assert body["ok"] is False

    def test_returns_agents_ordered_by_turn_order(self, client: TestClient):
        cid = _create_conversation(client)
        a1 = _create_agent(client, "Zulu", conversation_id=cid)
        a2 = _create_agent(client, "Alpha", conversation_id=cid)
        resp = client.get(f"/api/conversations/{cid}/agents")
        assert resp.status_code == 200
        agents = resp.json()["data"]["agents"]
        assert len(agents) == 2
        # First created gets turn_order=1, second gets turn_order=2
        assert agents[0]["id"] == a1["id"]
        assert agents[0]["turn_order"] == 1
        assert agents[1]["id"] == a2["id"]
        assert agents[1]["turn_order"] == 2

    def test_agents_include_all_agent_fields_plus_turn_order(self, client: TestClient):
        cid = _create_conversation(client)
        _create_agent(client, "Bot", conversation_id=cid)
        resp = client.get(f"/api/conversations/{cid}/agents")
        agent = resp.json()["data"]["agents"][0]
        # Must have standard agent fields
        for key in [
            "id",
            "display_name",
            "provider",
            "model",
            "role",
            "status",
            "created_at",
            "updated_at",
        ]:
            assert key in agent, f"Missing field: {key}"
        # Must have turn_order
        assert "turn_order" in agent


# ── UI-014b: POST /agents with optional conversation_id ───────────


class TestCreateAgentWithConversation:
    def test_create_agent_with_conversation_id_returns_turn_order(self, client: TestClient):
        cid = _create_conversation(client)
        agent = _create_agent(client, "A", conversation_id=cid)
        assert agent["turn_order"] == 1

    def test_turn_order_increments(self, client: TestClient):
        cid = _create_conversation(client)
        a1 = _create_agent(client, "A", conversation_id=cid)
        a2 = _create_agent(client, "B", conversation_id=cid)
        a3 = _create_agent(client, "C", conversation_id=cid)
        assert a1["turn_order"] == 1
        assert a2["turn_order"] == 2
        assert a3["turn_order"] == 3

    def test_create_agent_without_conversation_id_has_no_turn_order(self, client: TestClient):
        agent = _create_agent(client, "Global")
        # Global agents should not have turn_order (or it can be None)
        assert agent.get("turn_order") is None

    def test_create_agent_with_nonexistent_conversation_returns_404(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "X",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
                "conversation_id": "nonexistent",
            },
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_turn_order_scoped_per_conversation(self, client: TestClient):
        cid1 = _create_conversation(client, "Conv 1")
        cid2 = _create_conversation(client, "Conv 2")
        a1 = _create_agent(client, "A", conversation_id=cid1)
        a2 = _create_agent(client, "B", conversation_id=cid2)
        # Both should get turn_order=1 since they're in different conversations
        assert a1["turn_order"] == 1
        assert a2["turn_order"] == 1


# ── UI-014c: POST /conversations/{cid}/agents/{aid}/remove ────────


class TestRemoveAgentFromConversation:
    def test_remove_agent_from_conversation(self, client: TestClient):
        cid = _create_conversation(client)
        agent = _create_agent(client, "A", conversation_id=cid)
        resp = client.delete(f"/api/conversations/{cid}/agents/{agent['id']}")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        # Agent should no longer appear in conversation agents
        agents = client.get(f"/api/conversations/{cid}/agents").json()["data"]["agents"]
        assert len(agents) == 0
        # But agent itself should still exist globally
        all_agents = client.get("/api/agents").json()["data"]["agents"]
        assert any(a["id"] == agent["id"] for a in all_agents)

    def test_remove_nonexistent_link_returns_404(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.delete(f"/api/conversations/{cid}/agents/nonexistent")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_delete_agent_cascades_to_conversation_agent(self, client: TestClient):
        cid = _create_conversation(client)
        agent = _create_agent(client, "A", conversation_id=cid)
        # Delete the agent globally
        resp = client.post("/api/agents/delete", json={"agent_id": agent["id"]})
        assert resp.status_code == 200
        # Conversation should have no agents
        agents = client.get(f"/api/conversations/{cid}/agents").json()["data"]["agents"]
        assert len(agents) == 0


# ── UI-014d: PATCH /conversations/{cid}/agents/reorder ────────────


class TestReorderConversationAgents:
    def test_reorder_agents(self, client: TestClient):
        cid = _create_conversation(client)
        a1 = _create_agent(client, "A", conversation_id=cid)
        a2 = _create_agent(client, "B", conversation_id=cid)
        a3 = _create_agent(client, "C", conversation_id=cid)
        # Reverse the order
        resp = client.patch(
            f"/api/conversations/{cid}/agents/reorder",
            json={"agent_ids": [a3["id"], a2["id"], a1["id"]]},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        agents = body["data"]["agents"]
        assert len(agents) == 3
        assert agents[0]["id"] == a3["id"]
        assert agents[0]["turn_order"] == 1
        assert agents[1]["id"] == a2["id"]
        assert agents[1]["turn_order"] == 2
        assert agents[2]["id"] == a1["id"]
        assert agents[2]["turn_order"] == 3

    def test_reorder_with_mismatched_agent_ids_returns_400(self, client: TestClient):
        cid = _create_conversation(client)
        a1 = _create_agent(client, "A", conversation_id=cid)
        _create_agent(client, "B", conversation_id=cid)
        # Only provide one agent id instead of two
        resp = client.patch(
            f"/api/conversations/{cid}/agents/reorder",
            json={"agent_ids": [a1["id"]]},
        )
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_reorder_with_unknown_agent_id_returns_400(self, client: TestClient):
        cid = _create_conversation(client)
        _create_agent(client, "A", conversation_id=cid)
        resp = client.patch(
            f"/api/conversations/{cid}/agents/reorder",
            json={"agent_ids": ["unknown-id"]},
        )
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_reorder_nonexistent_conversation_returns_404(self, client: TestClient):
        resp = client.patch(
            "/api/conversations/nonexistent/agents/reorder",
            json={"agent_ids": []},
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

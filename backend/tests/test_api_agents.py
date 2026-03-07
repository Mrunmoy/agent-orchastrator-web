"""Tests for agent config CRUD API endpoints (API-004)."""

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


# ── GET /agents ────────────────────────────────────────────────────


class TestListAgents:
    def test_empty_list_initially(self, client: TestClient):
        resp = client.get("/api/agents")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["agents"] == []

    def test_list_after_creating_multiple(self, client: TestClient):
        client.post(
            "/api/agents",
            json={
                "display_name": "Bravo",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        client.post(
            "/api/agents",
            json={
                "display_name": "Alpha",
                "provider": "codex",
                "model": "codex-1",
                "role": "coordinator",
            },
        )
        body = client.get("/api/agents").json()
        agents = body["data"]["agents"]
        assert len(agents) == 2
        # Ordered by display_name
        assert agents[0]["display_name"] == "Alpha"
        assert agents[1]["display_name"] == "Bravo"


# ── POST /agents ───────────────────────────────────────────────────


class TestCreateAgent:
    def test_create_with_valid_data(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Agent A",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        agent = body["data"]["agent"]
        assert agent["display_name"] == "Agent A"
        assert agent["provider"] == "claude"
        assert agent["model"] == "opus"
        assert agent["role"] == "worker"
        assert agent["status"] == "idle"
        assert len(agent["id"]) == 36  # UUID
        assert agent["created_at"] is not None
        assert agent["updated_at"] is not None

    def test_create_with_all_optional_fields(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Agent B",
                "provider": "gemini",
                "model": "gemini-pro",
                "role": "moderator",
                "personality_key": "strict",
                "capabilities_json": '{"tools": ["search"]}',
            },
        )
        assert resp.status_code == 200
        agent = resp.json()["data"]["agent"]
        assert agent["personality_key"] == "strict"
        assert agent["capabilities_json"] == '{"tools": ["search"]}'

    def test_create_with_invalid_provider(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Bad",
                "provider": "invalid_provider",
                "model": "x",
                "role": "worker",
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert "provider" in body["error"].lower()

    def test_create_with_invalid_role(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Bad",
                "provider": "claude",
                "model": "x",
                "role": "invalid_role",
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert "role" in body["error"].lower()


# ── POST /agents/update ───────────────────────────────────────────


class TestUpdateAgent:
    def test_update_display_name(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Old Name",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent_id = resp.json()["data"]["agent"]["id"]
        resp = client.post(
            "/api/agents/update",
            json={"agent_id": agent_id, "display_name": "New Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert resp.json()["data"]["agent"]["display_name"] == "New Name"

    def test_update_provider(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Test",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent_id = resp.json()["data"]["agent"]["id"]
        resp = client.post(
            "/api/agents/update",
            json={"agent_id": agent_id, "provider": "codex"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["agent"]["provider"] == "codex"

    def test_update_nonexistent_agent(self, client: TestClient):
        resp = client.post(
            "/api/agents/update",
            json={"agent_id": "nonexistent", "display_name": "X"},
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_update_with_invalid_provider(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Test",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent_id = resp.json()["data"]["agent"]["id"]
        resp = client.post(
            "/api/agents/update",
            json={"agent_id": agent_id, "provider": "bad_provider"},
        )
        assert resp.status_code == 400
        assert resp.json()["ok"] is False


# ── POST /agents/delete ───────────────────────────────────────────


class TestDeleteAgent:
    def test_delete_agent(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Doomed",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent_id = resp.json()["data"]["agent"]["id"]
        resp = client.post("/api/agents/delete", json={"agent_id": agent_id})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert resp.json()["data"]["deleted_id"] == agent_id
        # Confirm gone from list
        agents = client.get("/api/agents").json()["data"]["agents"]
        assert len(agents) == 0

    def test_delete_nonexistent_agent(self, client: TestClient):
        resp = client.post("/api/agents/delete", json={"agent_id": "nonexistent"})
        assert resp.status_code == 404
        assert resp.json()["ok"] is False


# ── PATCH /agents/{agent_id}/order ─────────────────────────────────


class TestReorderAgent:
    def test_patch_order_returns_200_and_updates_sort_order(self, client: TestClient):
        resp = client.post(
            "/agents",
            json={
                "display_name": "Ordered Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent_id = resp.json()["data"]["agent"]["id"]
        resp = client.patch(f"/agents/{agent_id}/order", json={"sort_order": 3})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["agent"]["sort_order"] == 3

    def test_get_agents_includes_sort_order_field(self, client: TestClient):
        client.post(
            "/agents",
            json={
                "display_name": "Agent With Order",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        resp = client.get("/agents")
        agents = resp.json()["data"]["agents"]
        assert len(agents) == 1
        assert "sort_order" in agents[0]
        assert agents[0]["sort_order"] == 0

    def test_patch_negative_sort_order_returns_400(self, client: TestClient):
        resp = client.post(
            "/agents",
            json={
                "display_name": "Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent_id = resp.json()["data"]["agent"]["id"]
        resp = client.patch(f"/agents/{agent_id}/order", json={"sort_order": -1})
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False

    def test_patch_order_nonexistent_agent_returns_404(self, client: TestClient):
        resp = client.patch("/agents/nonexistent-id/order", json={"sort_order": 1})
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_create_agent_has_default_sort_order_zero(self, client: TestClient):
        resp = client.post(
            "/agents",
            json={
                "display_name": "New Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        agent = resp.json()["data"]["agent"]
        assert agent["sort_order"] == 0

    def test_get_agents_ordered_by_sort_order(self, client: TestClient):
        resp1 = client.post(
            "/agents",
            json={"display_name": "Beta", "provider": "claude", "model": "opus", "role": "worker"},
        )
        resp2 = client.post(
            "/agents",
            json={
                "display_name": "Alpha",
                "provider": "codex",
                "model": "codex-1",
                "role": "worker",
            },
        )
        agent1_id = resp1.json()["data"]["agent"]["id"]
        agent2_id = resp2.json()["data"]["agent"]["id"]
        # Set Beta to sort_order 0 and Alpha to sort_order 1
        client.patch(f"/agents/{agent1_id}/order", json={"sort_order": 0})
        client.patch(f"/agents/{agent2_id}/order", json={"sort_order": 1})
        agents = client.get("/agents").json()["data"]["agents"]
        # Beta (sort_order=0) should come before Alpha (sort_order=1)
        assert agents[0]["display_name"] == "Beta"
        assert agents[1]["display_name"] == "Alpha"

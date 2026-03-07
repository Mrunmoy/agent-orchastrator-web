"""Tests for conversation CRUD API endpoints (API-002)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agent_orchestrator.api import create_app
from agent_orchestrator.api.db_provider import _init_db, get_db


@pytest.fixture(autouse=True)
def _fresh_db():
    """Reset the in-memory database before each test."""
    _init_db()


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)


# ── GET /conversations ──────────────────────────────────────────────


class TestListConversations:
    def test_returns_200(self, client: TestClient):
        resp = client.get("/conversations")
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient):
        resp = client.get("/conversations")
        body = resp.json()
        assert body["ok"] is True

    def test_empty_list_initially(self, client: TestClient):
        body = client.get("/conversations").json()
        assert body["data"]["conversations"] == []

    def test_returns_created_conversation(self, client: TestClient):
        client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        body = client.get("/conversations").json()
        assert len(body["data"]["conversations"]) == 1
        assert body["data"]["conversations"][0]["title"] == "Test"

    def test_excludes_deleted(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Del", "project_path": "/tmp"},
        )
        cid = resp.json()["data"]["conversation"]["id"]
        client.post("/conversations/delete", json={"conversation_id": cid})
        body = client.get("/conversations").json()
        assert len(body["data"]["conversations"]) == 0

    def test_ordered_by_updated_at_desc(self, client: TestClient):
        client.post(
            "/conversations/new",
            json={"title": "First", "project_path": "/tmp"},
        )
        client.post(
            "/conversations/new",
            json={"title": "Second", "project_path": "/tmp"},
        )
        body = client.get("/conversations").json()
        titles = [c["title"] for c in body["data"]["conversations"]]
        assert titles == ["Second", "First"]


# ── POST /conversations/new ─────────────────────────────────────────


class TestCreateConversation:
    def test_returns_200(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        assert resp.json()["ok"] is True

    def test_returns_conversation_with_id(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        conv = resp.json()["data"]["conversation"]
        assert "id" in conv
        assert len(conv["id"]) == 36  # UUID format

    def test_defaults(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        conv = resp.json()["data"]["conversation"]
        assert conv["state"] == "debate"
        assert conv["phase"] == "design_debate"
        assert conv["gate_status"] == "open"
        assert conv["priority"] == 100
        assert conv["active"] == 0

    def test_timestamps_set(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        conv = resp.json()["data"]["conversation"]
        assert conv["created_at"] is not None
        assert conv["updated_at"] is not None
        assert conv["deleted_at"] is None


# ── POST /conversations/select ──────────────────────────────────────


class TestSelectConversation:
    def test_sets_active_flag(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Test", "project_path": "/tmp"},
        )
        cid = resp.json()["data"]["conversation"]["id"]
        resp = client.post("/conversations/select", json={"conversation_id": cid})
        assert resp.status_code == 200
        assert resp.json()["data"]["conversation"]["active"] == 1

    def test_deactivates_others(self, client: TestClient):
        r1 = client.post(
            "/conversations/new",
            json={"title": "A", "project_path": "/tmp"},
        )
        r2 = client.post(
            "/conversations/new",
            json={"title": "B", "project_path": "/tmp"},
        )
        cid_a = r1.json()["data"]["conversation"]["id"]
        cid_b = r2.json()["data"]["conversation"]["id"]
        client.post("/conversations/select", json={"conversation_id": cid_a})
        client.post("/conversations/select", json={"conversation_id": cid_b})
        convs = client.get("/conversations").json()["data"]["conversations"]
        active_map = {c["id"]: c["active"] for c in convs}
        assert active_map[cid_a] == 0
        assert active_map[cid_b] == 1

    def test_envelope_ok(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "X", "project_path": "/tmp"},
        )
        cid = resp.json()["data"]["conversation"]["id"]
        resp = client.post("/conversations/select", json={"conversation_id": cid})
        assert resp.json()["ok"] is True

    def test_404_for_missing(self, client: TestClient):
        resp = client.post(
            "/conversations/select",
            json={"conversation_id": "nonexistent"},
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False
        assert "error" in resp.json()

    def test_select_updates_only_selected_updated_at(self, client: TestClient):
        r1 = client.post(
            "/conversations/new",
            json={"title": "A", "project_path": "/tmp"},
        )
        r2 = client.post(
            "/conversations/new",
            json={"title": "B", "project_path": "/tmp"},
        )
        cid_a = r1.json()["data"]["conversation"]["id"]
        cid_b = r2.json()["data"]["conversation"]["id"]

        db = get_db()
        with db.connection() as conn:
            old_a = "2001-01-01T00:00:00+00:00"
            old_b = "2002-02-02T00:00:00+00:00"
            conn.execute("UPDATE conversation SET updated_at = ? WHERE id = ?", (old_a, cid_a))
            conn.execute("UPDATE conversation SET updated_at = ? WHERE id = ?", (old_b, cid_b))
            conn.commit()

        client.post("/conversations/select", json={"conversation_id": cid_a})

        convs = client.get("/conversations").json()["data"]["conversations"]
        by_id = {c["id"]: c for c in convs}
        assert by_id[cid_a]["updated_at"] != old_a
        assert by_id[cid_b]["updated_at"] == old_b
        assert convs[0]["id"] == cid_a


# ── POST /conversations/delete ──────────────────────────────────────


class TestDeleteConversation:
    def test_soft_deletes(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "Gone", "project_path": "/tmp"},
        )
        cid = resp.json()["data"]["conversation"]["id"]
        del_resp = client.post("/conversations/delete", json={"conversation_id": cid})
        assert del_resp.status_code == 200
        assert del_resp.json()["ok"] is True
        conv = del_resp.json()["data"]["conversation"]
        assert conv["deleted_at"] is not None

    def test_404_for_missing(self, client: TestClient):
        resp = client.post(
            "/conversations/delete",
            json={"conversation_id": "nonexistent"},
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False


# ── POST /conversations/clear-all ───────────────────────────────────


class TestClearAllConversations:
    def test_returns_count(self, client: TestClient):
        client.post(
            "/conversations/new",
            json={"title": "A", "project_path": "/tmp"},
        )
        client.post(
            "/conversations/new",
            json={"title": "B", "project_path": "/tmp"},
        )
        resp = client.post("/conversations/clear-all")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert resp.json()["data"]["deleted_count"] == 2

    def test_conversations_gone_after_clear(self, client: TestClient):
        client.post(
            "/conversations/new",
            json={"title": "A", "project_path": "/tmp"},
        )
        client.post("/conversations/clear-all")
        convs = client.get("/conversations").json()["data"]["conversations"]
        assert convs == []

    def test_zero_when_none(self, client: TestClient):
        resp = client.post("/conversations/clear-all")
        assert resp.json()["data"]["deleted_count"] == 0

    def test_does_not_redelete_already_deleted(self, client: TestClient):
        resp = client.post(
            "/conversations/new",
            json={"title": "A", "project_path": "/tmp"},
        )
        cid = resp.json()["data"]["conversation"]["id"]
        client.post("/conversations/delete", json={"conversation_id": cid})
        resp = client.post("/conversations/clear-all")
        assert resp.json()["data"]["deleted_count"] == 0

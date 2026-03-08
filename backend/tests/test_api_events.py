"""Tests for events endpoints (API-005 / T-204).

Covers GET /api/events, GET /api/events/latest, POST /api/events,
all backed by SQLiteMessageEventRepository with JSONL fallback.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

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


def _create_conversation(client: TestClient, title: str = "Test") -> str:
    """Helper: create a conversation and return its id."""
    resp = client.post(
        "/api/conversations/new",
        json={"title": title, "project_path": "/tmp"},
    )
    return resp.json()["data"]["conversation"]["id"]


def _seed_agent(agent_id: str = "agent-1") -> None:
    """Insert a minimal agent row for FK references."""
    db = get_db()
    now = datetime.now(UTC).isoformat()
    with db.connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO agent "
            "(id, display_name, provider, model, role, status, capabilities_json, "
            "sort_order, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (agent_id, agent_id, "claude", "opus-4", "worker", "idle", "[]", 0, now, now),
        )
        conn.commit()


def _insert_event(
    conversation_id: str,
    text: str = "hello",
    source_type: str = "agent",
    event_type: str = "chat_message",
    source_id: str | None = None,
) -> str:
    """Insert a message_event directly and return the event_id."""
    event_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    db = get_db()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO message_event "
            "(conversation_id, event_id, source_type, source_id, "
            "text, event_type, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (conversation_id, event_id, source_type, source_id, text, event_type, now),
        )
        conn.commit()
    return event_id


# ── GET /api/events ──────────────────────────────────────────────


class TestGetEvents:
    def test_requires_conversation_id(self, client: TestClient):
        resp = client.get("/api/events")
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_returns_events_for_conversation(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_event(cid, text="msg1")
        _insert_event(cid, text="msg2")

        resp = client.get("/api/events", params={"conversation_id": cid})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        events = body["data"]["events"]
        assert len(events) == 2
        texts = [e["text"] for e in events]
        assert "msg1" in texts
        assert "msg2" in texts

    def test_returns_empty_for_no_events(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.get("/api/events", params={"conversation_id": cid})
        assert resp.status_code == 200
        assert resp.json()["data"]["events"] == []

    def test_pagination_limit(self, client: TestClient):
        cid = _create_conversation(client)
        for i in range(5):
            _insert_event(cid, text=f"msg-{i}")

        resp = client.get("/api/events", params={"conversation_id": cid, "limit": 3})
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 3

    def test_pagination_offset(self, client: TestClient):
        cid = _create_conversation(client)
        for i in range(5):
            _insert_event(cid, text=f"msg-{i}")

        resp = client.get("/api/events", params={"conversation_id": cid, "offset": 2})
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 3  # 5 total - 2 offset = 3 remaining (default limit 100)

    def test_pagination_limit_and_offset(self, client: TestClient):
        cid = _create_conversation(client)
        for i in range(5):
            _insert_event(cid, text=f"msg-{i}")

        resp = client.get(
            "/api/events",
            params={"conversation_id": cid, "limit": 2, "offset": 1},
        )
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 2
        assert events[0]["text"] == "msg-1"
        assert events[1]["text"] == "msg-2"

    def test_does_not_return_other_conversations(self, client: TestClient):
        cid1 = _create_conversation(client, title="Conv 1")
        cid2 = _create_conversation(client, title="Conv 2")
        _insert_event(cid1, text="conv1-msg")
        _insert_event(cid2, text="conv2-msg")

        resp = client.get("/api/events", params={"conversation_id": cid1})
        events = resp.json()["data"]["events"]
        assert len(events) == 1
        assert events[0]["text"] == "conv1-msg"

    def test_since_filters_after_event_id(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_event(cid, text="msg-0")
        since_id = _insert_event(cid, text="msg-1")
        _insert_event(cid, text="msg-2")

        resp = client.get(
            "/api/events",
            params={"conversation_id": cid, "since": since_id},
        )
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 1
        assert events[0]["text"] == "msg-2"

    def test_since_unknown_id_returns_all(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_event(cid, text="msg-0")
        _insert_event(cid, text="msg-1")

        resp = client.get(
            "/api/events",
            params={"conversation_id": cid, "since": "nonexistent"},
        )
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 2


# ── GET /api/events/latest ───────────────────────────────────────


class TestGetLatestEvents:
    def test_requires_conversation_id(self, client: TestClient):
        resp = client.get("/api/events/latest")
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_returns_last_n_events(self, client: TestClient):
        cid = _create_conversation(client)
        for i in range(10):
            _insert_event(cid, text=f"msg-{i}")

        resp = client.get("/api/events/latest", params={"conversation_id": cid, "n": 3})
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 3
        texts = [e["text"] for e in events]
        assert texts == ["msg-7", "msg-8", "msg-9"]

    def test_returns_all_when_n_exceeds_total(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_event(cid, text="only-one")

        resp = client.get("/api/events/latest", params={"conversation_id": cid, "n": 50})
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 1

    def test_default_n_is_10(self, client: TestClient):
        cid = _create_conversation(client)
        for i in range(15):
            _insert_event(cid, text=f"msg-{i}")

        resp = client.get("/api/events/latest", params={"conversation_id": cid})
        assert resp.status_code == 200
        events = resp.json()["data"]["events"]
        assert len(events) == 10

    def test_rejects_non_positive_n(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.get("/api/events/latest", params={"conversation_id": cid, "n": 0})
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_rejects_negative_n(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.get("/api/events/latest", params={"conversation_id": cid, "n": -5})
        assert resp.status_code == 400
        assert resp.json()["ok"] is False


# ── POST /api/events ─────────────────────────────────────────────


class TestPostEvent:
    def test_appends_event(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            "/api/events",
            json={
                "conversation_id": cid,
                "source_type": "agent",
                "text": "Hello world",
                "event_type": "chat_message",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        event = body["data"]["event"]
        assert event["text"] == "Hello world"
        assert event["conversation_id"] == cid
        assert event["event_type"] == "chat_message"
        assert event["source_type"] == "agent"
        assert event["event_id"] is not None

    def test_appends_with_optional_fields(self, client: TestClient):
        cid = _create_conversation(client)
        _seed_agent("agent-1")
        resp = client.post(
            "/api/events",
            json={
                "conversation_id": cid,
                "source_type": "agent",
                "source_id": "agent-1",
                "text": "With source",
                "event_type": "debate_turn",
                "metadata_json": '{"round": 1}',
            },
        )
        assert resp.status_code == 200
        event = resp.json()["data"]["event"]
        assert event["source_id"] == "agent-1"
        assert event["metadata_json"] == '{"round": 1}'

    def test_requires_conversation_id(self, client: TestClient):
        resp = client.post(
            "/api/events",
            json={
                "source_type": "agent",
                "text": "Hello",
                "event_type": "chat_message",
            },
        )
        assert resp.status_code == 422

    def test_requires_text(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            "/api/events",
            json={
                "conversation_id": cid,
                "source_type": "agent",
                "event_type": "chat_message",
            },
        )
        assert resp.status_code == 422

    def test_event_persisted_in_db(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            "/api/events",
            json={
                "conversation_id": cid,
                "source_type": "user",
                "text": "Persisted event",
                "event_type": "steer",
            },
        )
        event_id = resp.json()["data"]["event"]["event_id"]

        # Verify via GET endpoint
        resp2 = client.get("/api/events", params={"conversation_id": cid})
        events = resp2.json()["data"]["events"]
        assert any(e["event_id"] == event_id for e in events)

    def test_event_visible_in_latest(self, client: TestClient):
        cid = _create_conversation(client)
        client.post(
            "/api/events",
            json={
                "conversation_id": cid,
                "source_type": "agent",
                "text": "Latest event",
                "event_type": "chat_message",
            },
        )
        resp = client.get("/api/events/latest", params={"conversation_id": cid, "n": 1})
        events = resp.json()["data"]["events"]
        assert len(events) == 1
        assert events[0]["text"] == "Latest event"


# ── Steer endpoint uses repo ─────────────────────────────────────


class TestSteerUsesRepo:
    """Verify the steer endpoint still works after refactoring to use the repo."""

    def test_steer_event_readable_via_events_endpoint(self, client: TestClient):
        cid = _create_conversation(client)
        client.post(
            f"/api/orchestration/{cid}/steer",
            json={"note": "Focus on tests"},
        )
        resp = client.get("/api/events", params={"conversation_id": cid})
        events = resp.json()["data"]["events"]
        assert len(events) == 1
        assert events[0]["text"] == "Focus on tests"
        assert events[0]["event_type"] == "steering"

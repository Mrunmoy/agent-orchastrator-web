"""Tests for the events stream endpoint (API-005)."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from agent_orchestrator.api import app
from agent_orchestrator.storage.event_log import EventLogWriter

client = TestClient(app)


def _write_events(path, events: list[dict]) -> None:
    """Helper: write events to a JSONL file using EventLogWriter."""
    with EventLogWriter(path) as writer:
        for ev in events:
            writer.append(ev)


class TestEventsEndpoint:
    """GET /events returns events for a conversation."""

    def test_missing_conversation_id_returns_error(self):
        resp = client.get("/events")
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert "conversation_id" in body["error"].lower()

    def test_empty_conversation_returns_empty_list(self, tmp_path):
        conv_id = "empty-conv-001"
        log_path = tmp_path / f"{conv_id}.jsonl"
        # Don't create the file — reader returns [] for missing files
        with patch(
            "agent_orchestrator.api.routes.events.conversation_log_path",
            return_value=log_path,
        ):
            resp = client.get(f"/events?conversation_id={conv_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["events"] == []

    def test_returns_all_events_for_conversation(self, tmp_path):
        conv_id = "conv-all-001"
        log_path = tmp_path / f"{conv_id}.jsonl"
        events = [
            {"event_id": "e1", "type": "msg", "timestamp": "2026-01-01T00:00:01Z"},
            {"event_id": "e2", "type": "msg", "timestamp": "2026-01-01T00:00:02Z"},
            {"event_id": "e3", "type": "msg", "timestamp": "2026-01-01T00:00:03Z"},
        ]
        _write_events(log_path, events)
        with patch(
            "agent_orchestrator.api.routes.events.conversation_log_path",
            return_value=log_path,
        ):
            resp = client.get(f"/events?conversation_id={conv_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]["events"]) == 3
        assert body["data"]["events"][0]["event_id"] == "e1"
        assert body["data"]["events"][2]["event_id"] == "e3"

    def test_since_parameter_filters_events(self, tmp_path):
        conv_id = "conv-since-001"
        log_path = tmp_path / f"{conv_id}.jsonl"
        events = [
            {"event_id": "e1", "type": "msg", "timestamp": "2026-01-01T00:00:01Z"},
            {"event_id": "e2", "type": "msg", "timestamp": "2026-01-01T00:00:02Z"},
            {"event_id": "e3", "type": "msg", "timestamp": "2026-01-01T00:00:03Z"},
        ]
        _write_events(log_path, events)
        with patch(
            "agent_orchestrator.api.routes.events.conversation_log_path",
            return_value=log_path,
        ):
            resp = client.get(f"/events?conversation_id={conv_id}&since=e1")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]["events"]) == 2
        assert body["data"]["events"][0]["event_id"] == "e2"
        assert body["data"]["events"][1]["event_id"] == "e3"

    def test_events_sorted_by_timestamp_ascending(self, tmp_path):
        conv_id = "conv-sort-001"
        log_path = tmp_path / f"{conv_id}.jsonl"
        # Write in order — reader preserves file order which is chronological
        events = [
            {"event_id": "e1", "type": "msg", "timestamp": "2026-01-01T00:00:01Z"},
            {"event_id": "e2", "type": "msg", "timestamp": "2026-01-01T00:00:05Z"},
            {"event_id": "e3", "type": "msg", "timestamp": "2026-01-01T00:00:03Z"},
        ]
        _write_events(log_path, events)
        with patch(
            "agent_orchestrator.api.routes.events.conversation_log_path",
            return_value=log_path,
        ):
            resp = client.get(f"/events?conversation_id={conv_id}")
        body = resp.json()
        timestamps = [e["timestamp"] for e in body["data"]["events"]]
        assert timestamps == sorted(timestamps)


class TestLatestEndpoint:
    """GET /events/latest returns the last N events."""

    def test_missing_conversation_id_returns_error(self):
        resp = client.get("/events/latest")
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert "conversation_id" in body["error"].lower()

    def test_returns_last_n_events(self, tmp_path):
        conv_id = "conv-latest-001"
        log_path = tmp_path / f"{conv_id}.jsonl"
        events = [
            {"event_id": f"e{i}", "type": "msg", "timestamp": f"2026-01-01T00:00:{i:02d}Z"}
            for i in range(1, 6)
        ]
        _write_events(log_path, events)
        with patch(
            "agent_orchestrator.api.routes.events.conversation_log_path",
            return_value=log_path,
        ):
            resp = client.get(f"/events/latest?conversation_id={conv_id}&n=2")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]["events"]) == 2
        assert body["data"]["events"][0]["event_id"] == "e4"
        assert body["data"]["events"][1]["event_id"] == "e5"

    def test_default_n_is_10(self, tmp_path):
        conv_id = "conv-default-001"
        log_path = tmp_path / f"{conv_id}.jsonl"
        events = [
            {"event_id": f"e{i}", "type": "msg", "timestamp": f"2026-01-01T00:00:{i:02d}Z"}
            for i in range(1, 16)  # 15 events
        ]
        _write_events(log_path, events)
        with patch(
            "agent_orchestrator.api.routes.events.conversation_log_path",
            return_value=log_path,
        ):
            resp = client.get(f"/events/latest?conversation_id={conv_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]["events"]) == 10
        # Should be events e6 through e15
        assert body["data"]["events"][0]["event_id"] == "e6"
        assert body["data"]["events"][9]["event_id"] == "e15"

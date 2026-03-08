"""Tests for orchestration control endpoints (API-003)."""

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


def _insert_run(
    conversation_id: str,
    status: str = "running",
    batch_size: int = 20,
) -> str:
    """Helper: insert a scheduler_run row and return its id."""
    run_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    db = get_db()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO scheduler_run "
            "(id, conversation_id, status, batch_size, created_at, started_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, conversation_id, status, batch_size, now, now),
        )
        conn.commit()
    return run_id


# ── POST /orchestration/{conversation_id}/run ─────────────────────


class TestRunEndpoint:
    def test_returns_200_and_creates_run(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(f"/api/orchestration/{cid}/run")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        run = body["data"]["run"]
        assert run["conversation_id"] == cid
        assert run["status"] == "queued"
        assert run["batch_size"] == 20

    def test_custom_batch_size(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            f"/api/orchestration/{cid}/run",
            json={"batch_size": 10},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["run"]["batch_size"] == 10

    def test_404_for_missing_conversation(self, client: TestClient):
        resp = client.post("/api/orchestration/nonexistent/run")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_409_if_already_running(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="running")
        resp = client.post(f"/api/orchestration/{cid}/run")
        assert resp.status_code == 409
        assert resp.json()["ok"] is False

    def test_409_if_paused_run_exists(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="paused")
        resp = client.post(f"/api/orchestration/{cid}/run")
        assert resp.status_code == 409
        assert resp.json()["ok"] is False

    def test_422_for_zero_batch_size(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            f"/api/orchestration/{cid}/run",
            json={"batch_size": 0},
        )
        assert resp.status_code == 422

    def test_422_for_negative_batch_size(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            f"/api/orchestration/{cid}/run",
            json={"batch_size": -5},
        )
        assert resp.status_code == 422

    def test_run_persisted_in_db(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(f"/api/orchestration/{cid}/run")
        run_id = resp.json()["data"]["run"]["id"]
        db = get_db()
        with db.connection() as conn:
            row = conn.execute(
                "SELECT id, status FROM scheduler_run WHERE id = ?",
                (run_id,),
            ).fetchone()
        assert row is not None
        assert row[1] == "queued"


# ── POST /orchestration/{conversation_id}/continue ────────────────


class TestContinueEndpoint:
    def test_continues_paused_run(self, client: TestClient):
        cid = _create_conversation(client)
        run_id = _insert_run(cid, status="paused")
        resp = client.post(f"/api/orchestration/{cid}/continue")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["run"]["status"] == "queued"
        assert body["data"]["run"]["id"] == run_id

    def test_404_for_missing_conversation(self, client: TestClient):
        resp = client.post("/api/orchestration/nonexistent/continue")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_409_if_no_paused_run(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(f"/api/orchestration/{cid}/continue")
        assert resp.status_code == 409
        assert resp.json()["ok"] is False

    def test_409_if_run_is_running(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="running")
        resp = client.post(f"/api/orchestration/{cid}/continue")
        assert resp.status_code == 409
        assert resp.json()["ok"] is False


# ── POST /orchestration/{conversation_id}/stop ────────────────────


class TestStopEndpoint:
    def test_stops_running_run(self, client: TestClient):
        cid = _create_conversation(client)
        run_id = _insert_run(cid, status="running")
        resp = client.post(f"/api/orchestration/{cid}/stop")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["run"]["status"] == "done"
        assert body["data"]["run"]["id"] == run_id

    def test_stops_paused_run(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="paused")
        resp = client.post(f"/api/orchestration/{cid}/stop")
        assert resp.status_code == 200
        assert resp.json()["data"]["run"]["status"] == "done"

    def test_stops_queued_run(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="queued")
        resp = client.post(f"/api/orchestration/{cid}/stop")
        assert resp.status_code == 200
        assert resp.json()["data"]["run"]["status"] == "done"

    def test_404_for_missing_conversation(self, client: TestClient):
        resp = client.post("/api/orchestration/nonexistent/stop")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_409_if_no_active_run(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(f"/api/orchestration/{cid}/stop")
        assert resp.status_code == 409
        assert resp.json()["ok"] is False

    def test_ended_at_set(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="running")
        resp = client.post(f"/api/orchestration/{cid}/stop")
        run = resp.json()["data"]["run"]
        assert run["ended_at"] is not None


# ── POST /orchestration/{conversation_id}/steer ───────────────────


class TestSteerEndpoint:
    def test_injects_steering_note(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            f"/api/orchestration/{cid}/steer",
            json={"note": "Focus on testing first"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["event"]["text"] == "Focus on testing first"
        assert body["data"]["event"]["source_type"] == "user"
        assert body["data"]["event"]["event_type"] == "steering"

    def test_404_for_missing_conversation(self, client: TestClient):
        resp = client.post(
            "/api/orchestration/nonexistent/steer",
            json={"note": "Hello"},
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_422_for_missing_note(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(f"/api/orchestration/{cid}/steer", json={})
        assert resp.status_code == 422

    def test_422_for_empty_note(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.post(
            f"/api/orchestration/{cid}/steer",
            json={"note": ""},
        )
        assert resp.status_code == 422

    def test_steering_persisted_as_message_event(self, client: TestClient):
        cid = _create_conversation(client)
        client.post(
            f"/api/orchestration/{cid}/steer",
            json={"note": "Persist this"},
        )
        db = get_db()
        with db.connection() as conn:
            row = conn.execute(
                "SELECT text, event_type, source_type FROM message_event "
                "WHERE conversation_id = ?",
                (cid,),
            ).fetchone()
        assert row is not None
        assert row[0] == "Persist this"
        assert row[1] == "steering"
        assert row[2] == "user"


# ── GET /orchestration/{conversation_id}/status ───────────────────


class TestStatusEndpoint:
    def test_returns_latest_run(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="done")
        run_id = _insert_run(cid, status="running")
        resp = client.get(f"/api/orchestration/{cid}/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        run = body["data"]["run"]
        assert run["id"] == run_id
        assert run["status"] == "running"

    def test_returns_null_when_no_runs(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.get(f"/api/orchestration/{cid}/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["run"] is None

    def test_404_for_missing_conversation(self, client: TestClient):
        resp = client.get("/api/orchestration/nonexistent/status")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_response_contains_all_run_fields(self, client: TestClient):
        cid = _create_conversation(client)
        _insert_run(cid, status="running", batch_size=15)
        resp = client.get(f"/api/orchestration/{cid}/status")
        run = resp.json()["data"]["run"]
        assert run["conversation_id"] == cid
        assert run["batch_size"] == 15
        assert "started_at" in run
        assert "created_at" in run

    def test_response_includes_frontend_fields(self, client: TestClient):
        """Ensure run_id, turns_completed, turns_total, updated_at are present."""
        cid = _create_conversation(client)
        _insert_run(cid, status="running", batch_size=10)
        resp = client.get(f"/api/orchestration/{cid}/status")
        run = resp.json()["data"]["run"]
        assert run["run_id"] == run["id"]
        assert run["turns_completed"] == 0
        assert run["turns_total"] == 10
        assert run["updated_at"] is not None

    def test_turns_completed_counts_message_events(self, client: TestClient):
        """turns_completed should reflect actual message_event rows for this run."""
        cid = _create_conversation(client)
        run_id = _insert_run(cid, status="running", batch_size=10)
        # Insert 3 message_events tied to this run via metadata_json
        db = get_db()
        now = datetime.now(UTC).isoformat()
        with db.connection() as conn:
            for i in range(3):
                eid = str(uuid.uuid4())
                meta = f'{{"turn_number": {i + 1}, "run_id": "{run_id}"}}'
                conn.execute(
                    "INSERT INTO message_event "
                    "(conversation_id, event_id, source_type, source_id, "
                    " text, event_type, metadata_json, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (cid, eid, "agent", None, "resp", "debate_turn", meta, now),
                )
            conn.commit()
        resp = client.get(f"/api/orchestration/{cid}/status")
        run = resp.json()["data"]["run"]
        assert run["turns_completed"] == 3


# ── GET /orchestration/{conversation_id}/runs ─────────────────────


class TestRunsListEndpoint:
    def test_returns_all_runs_ordered_desc(self, client: TestClient):
        cid = _create_conversation(client)
        first_id = _insert_run(cid, status="done")
        second_id = _insert_run(cid, status="running")
        resp = client.get(f"/api/orchestration/{cid}/runs")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        runs = body["data"]["runs"]
        assert len(runs) == 2
        # Most recent first
        assert runs[0]["id"] == second_id
        assert runs[1]["id"] == first_id

    def test_returns_empty_list_when_no_runs(self, client: TestClient):
        cid = _create_conversation(client)
        resp = client.get(f"/api/orchestration/{cid}/runs")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["runs"] == []

    def test_404_for_missing_conversation(self, client: TestClient):
        resp = client.get("/api/orchestration/nonexistent/runs")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

    def test_limited_to_20_runs(self, client: TestClient):
        cid = _create_conversation(client)
        for _ in range(25):
            _insert_run(cid, status="done")
        resp = client.get(f"/api/orchestration/{cid}/runs")
        runs = resp.json()["data"]["runs"]
        assert len(runs) == 20

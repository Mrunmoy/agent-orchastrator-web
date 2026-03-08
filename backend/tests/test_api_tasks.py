"""Tests for task CRUD API endpoints (T-202)."""

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


@pytest.fixture()
def conversation_id(client: TestClient) -> str:
    """Create a conversation and return its id."""
    resp = client.post(
        "/api/conversations/new",
        json={"title": "Test Conv", "project_path": "/tmp"},
    )
    return resp.json()["data"]["conversation"]["id"]


@pytest.fixture()
def task_id(client: TestClient, conversation_id: str) -> str:
    """Create a task and return its id."""
    resp = client.post(
        "/api/tasks",
        json={
            "conversation_id": conversation_id,
            "title": "Test Task",
            "spec_json": '{"goal": "test"}',
        },
    )
    return resp.json()["data"]["task"]["id"]


@pytest.fixture()
def agent_id(client: TestClient) -> str:
    """Create an agent and return its id."""
    resp = client.post(
        "/api/agents",
        json={
            "display_name": "TestBot",
            "provider": "claude",
            "model": "opus",
            "role": "worker",
        },
    )
    return resp.json()["data"]["agent"]["id"]


# -- POST /api/tasks --------------------------------------------------------


class TestCreateTask:
    def test_returns_200(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/tasks",
            json={
                "conversation_id": conversation_id,
                "title": "My Task",
                "spec_json": "{}",
            },
        )
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/tasks",
            json={
                "conversation_id": conversation_id,
                "title": "My Task",
                "spec_json": "{}",
            },
        )
        assert resp.json()["ok"] is True

    def test_returns_task_with_id(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/tasks",
            json={
                "conversation_id": conversation_id,
                "title": "My Task",
                "spec_json": "{}",
            },
        )
        task = resp.json()["data"]["task"]
        assert "id" in task
        assert len(task["id"]) == 36  # UUID

    def test_defaults(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/tasks",
            json={
                "conversation_id": conversation_id,
                "title": "My Task",
                "spec_json": "{}",
            },
        )
        task = resp.json()["data"]["task"]
        assert task["status"] == "todo"
        assert task["priority"] == 100
        assert task["depends_on_json"] == "[]"

    def test_custom_priority(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/tasks",
            json={
                "conversation_id": conversation_id,
                "title": "Urgent",
                "spec_json": "{}",
                "priority": 10,
            },
        )
        assert resp.json()["data"]["task"]["priority"] == 10

    def test_depends_on(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/tasks",
            json={
                "conversation_id": conversation_id,
                "title": "Dep Task",
                "spec_json": "{}",
                "depends_on": ["abc-123"],
            },
        )
        task = resp.json()["data"]["task"]
        assert task["depends_on_json"] == '["abc-123"]'


# -- GET /api/tasks?conversation_id=X ---------------------------------------


class TestListTasks:
    def test_returns_200(self, client: TestClient, conversation_id: str):
        resp = client.get(f"/api/tasks?conversation_id={conversation_id}")
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient, conversation_id: str):
        resp = client.get(f"/api/tasks?conversation_id={conversation_id}")
        assert resp.json()["ok"] is True

    def test_empty_initially(self, client: TestClient, conversation_id: str):
        body = client.get(f"/api/tasks?conversation_id={conversation_id}").json()
        assert body["data"]["tasks"] == []

    def test_returns_created_task(self, client: TestClient, conversation_id: str, task_id: str):
        body = client.get(f"/api/tasks?conversation_id={conversation_id}").json()
        assert len(body["data"]["tasks"]) == 1
        assert body["data"]["tasks"][0]["id"] == task_id

    def test_status_filter(self, client: TestClient, conversation_id: str, task_id: str):
        # task is in 'todo' — filter for 'done' should return nothing
        body = client.get(f"/api/tasks?conversation_id={conversation_id}&status=done").json()
        assert body["data"]["tasks"] == []

        # filter for 'todo' should return the task
        body = client.get(f"/api/tasks?conversation_id={conversation_id}&status=todo").json()
        assert len(body["data"]["tasks"]) == 1

    def test_invalid_status_filter(self, client: TestClient, conversation_id: str):
        resp = client.get(f"/api/tasks?conversation_id={conversation_id}&status=bogus")
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_missing_conversation_id(self, client: TestClient):
        resp = client.get("/api/tasks")
        assert resp.status_code == 422  # FastAPI validation error


# -- GET /api/tasks/{task_id} -----------------------------------------------


class TestGetTask:
    def test_returns_200(self, client: TestClient, task_id: str):
        resp = client.get(f"/api/tasks/{task_id}")
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient, task_id: str):
        resp = client.get(f"/api/tasks/{task_id}")
        assert resp.json()["ok"] is True

    def test_returns_correct_task(self, client: TestClient, task_id: str, conversation_id: str):
        task = client.get(f"/api/tasks/{task_id}").json()["data"]["task"]
        assert task["id"] == task_id
        assert task["conversation_id"] == conversation_id
        assert task["title"] == "Test Task"

    def test_404_for_missing(self, client: TestClient):
        resp = client.get("/api/tasks/nonexistent")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False


# -- PATCH /api/tasks/{task_id}/status --------------------------------------


class TestUpdateTaskStatus:
    def test_returns_200(self, client: TestClient, task_id: str):
        resp = client.patch(f"/api/tasks/{task_id}/status", json={"status": "design"})
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient, task_id: str):
        resp = client.patch(f"/api/tasks/{task_id}/status", json={"status": "design"})
        assert resp.json()["ok"] is True

    def test_updates_status(self, client: TestClient, task_id: str):
        client.patch(f"/api/tasks/{task_id}/status", json={"status": "design"})
        task = client.get(f"/api/tasks/{task_id}").json()["data"]["task"]
        assert task["status"] == "design"

    def test_invalid_status(self, client: TestClient, task_id: str):
        resp = client.patch(f"/api/tasks/{task_id}/status", json={"status": "bogus"})
        assert resp.status_code == 400
        assert resp.json()["ok"] is False

    def test_404_for_missing(self, client: TestClient):
        resp = client.patch("/api/tasks/nonexistent/status", json={"status": "design"})
        assert resp.status_code == 404
        assert resp.json()["ok"] is False


# -- PATCH /api/tasks/{task_id}/owner ---------------------------------------


class TestAssignOwner:
    def test_returns_200(self, client: TestClient, task_id: str, agent_id: str):
        resp = client.patch(f"/api/tasks/{task_id}/owner", json={"agent_id": agent_id})
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient, task_id: str, agent_id: str):
        resp = client.patch(f"/api/tasks/{task_id}/owner", json={"agent_id": agent_id})
        assert resp.json()["ok"] is True

    def test_assigns_owner(self, client: TestClient, task_id: str, agent_id: str):
        client.patch(f"/api/tasks/{task_id}/owner", json={"agent_id": agent_id})
        task = client.get(f"/api/tasks/{task_id}").json()["data"]["task"]
        assert task["owner_agent_id"] == agent_id

    def test_404_for_missing(self, client: TestClient, agent_id: str):
        resp = client.patch("/api/tasks/nonexistent/owner", json={"agent_id": agent_id})
        assert resp.status_code == 404
        assert resp.json()["ok"] is False


# -- PATCH /api/tasks/{task_id}/result --------------------------------------


class TestUpdateResult:
    def test_returns_200(self, client: TestClient, task_id: str):
        resp = client.patch(
            f"/api/tasks/{task_id}/result",
            json={"result_summary": "All good", "evidence_json": "[]"},
        )
        assert resp.status_code == 200

    def test_envelope_ok(self, client: TestClient, task_id: str):
        resp = client.patch(
            f"/api/tasks/{task_id}/result",
            json={"result_summary": "Done", "evidence_json": "[]"},
        )
        assert resp.json()["ok"] is True

    def test_updates_result(self, client: TestClient, task_id: str):
        client.patch(
            f"/api/tasks/{task_id}/result",
            json={
                "result_summary": "Implemented feature X",
                "evidence_json": '[{"test": "passed"}]',
            },
        )
        task = client.get(f"/api/tasks/{task_id}").json()["data"]["task"]
        assert task["result_summary"] == "Implemented feature X"
        assert task["evidence_json"] == '[{"test": "passed"}]'

    def test_404_for_missing(self, client: TestClient):
        resp = client.patch(
            "/api/tasks/nonexistent/result",
            json={"result_summary": "x", "evidence_json": "[]"},
        )
        assert resp.status_code == 404
        assert resp.json()["ok"] is False

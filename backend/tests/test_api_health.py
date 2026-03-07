"""Tests for the health and state API endpoints."""

from fastapi.testclient import TestClient

from agent_orchestrator.api import app

client = TestClient(app)


class TestHealthEndpoint:
    """GET /health returns liveness/readiness status."""

    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_envelope_ok(self):
        response = client.get("/health")
        body = response.json()
        assert body["ok"] is True

    def test_health_data_status(self):
        response = client.get("/health")
        body = response.json()
        assert body["data"]["status"] == "healthy"

    def test_health_no_error_key(self):
        response = client.get("/health")
        body = response.json()
        assert "error" not in body


class TestStateEndpoint:
    """GET /state returns app version and status."""

    def test_state_returns_200(self):
        response = client.get("/state")
        assert response.status_code == 200

    def test_state_envelope_ok(self):
        response = client.get("/state")
        body = response.json()
        assert body["ok"] is True

    def test_state_contains_version(self):
        response = client.get("/state")
        body = response.json()
        assert "version" in body["data"]
        assert isinstance(body["data"]["version"], str)
        assert len(body["data"]["version"]) > 0

    def test_state_contains_status(self):
        response = client.get("/state")
        body = response.json()
        assert body["data"]["status"] == "idle"

    def test_state_no_error_key(self):
        response = client.get("/state")
        body = response.json()
        assert "error" not in body

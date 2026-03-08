"""Tests for personality_key validation on agent create/update (T-206)."""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from agent_orchestrator.api import create_app
from agent_orchestrator.api.db_provider import _init_db
from agent_orchestrator.config import reset_config
from agent_orchestrator.config_loaders.personalities import _clear_cache

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SAMPLE_PERSONALITIES = {
    "software_developer": {
        "label": "Software Developer",
        "traits": ["pragmatic"],
        "instruction": "Act like a senior software engineer.",
    },
    "code_reviewer": {
        "label": "Code Reviewer",
        "traits": ["detail-oriented"],
        "instruction": "Prioritize bug risks.",
    },
}


@pytest.fixture(autouse=True)
def _fresh_state(tmp_path):
    """Reset DB and personality cache; point to a temp personalities file."""
    # Write a known personalities file
    p_file = tmp_path / "personalities.json"
    p_file.write_text(json.dumps(_SAMPLE_PERSONALITIES))
    os.environ["PERSONALITIES_PATH"] = str(p_file)

    _clear_cache()
    reset_config()  # re-read env so PERSONALITIES_PATH takes effect
    _init_db()
    yield
    _clear_cache()


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)


def _create_agent(client: TestClient, **overrides) -> dict:
    payload = {
        "display_name": "Test Agent",
        "provider": "claude",
        "model": "opus",
        "role": "worker",
    }
    payload.update(overrides)
    return client.post("/api/agents", json=payload).json()


# ---------------------------------------------------------------------------
# Create tests
# ---------------------------------------------------------------------------


class TestCreateAgentPersonality:
    def test_create_with_valid_personality_key(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Dev Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
                "personality_key": "software_developer",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["agent"]["personality_key"] == "software_developer"

    def test_create_with_invalid_personality_key_returns_400(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Bad Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
                "personality_key": "nonexistent_personality",
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert "personality" in body["error"].lower()

    def test_create_with_no_personality_key_succeeds(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Plain Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["agent"]["personality_key"] is None

    def test_create_with_null_personality_key_succeeds(self, client: TestClient):
        resp = client.post(
            "/api/agents",
            json={
                "display_name": "Null Key Agent",
                "provider": "claude",
                "model": "opus",
                "role": "worker",
                "personality_key": None,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True


# ---------------------------------------------------------------------------
# Update tests
# ---------------------------------------------------------------------------


class TestUpdateAgentPersonality:
    def test_update_with_valid_personality_key(self, client: TestClient):
        created = _create_agent(client)
        agent_id = created["data"]["agent"]["id"]

        resp = client.post(
            "/api/agents/update",
            json={"agent_id": agent_id, "personality_key": "code_reviewer"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["agent"]["personality_key"] == "code_reviewer"

    def test_update_with_invalid_personality_key_returns_400(self, client: TestClient):
        created = _create_agent(client)
        agent_id = created["data"]["agent"]["id"]

        resp = client.post(
            "/api/agents/update",
            json={"agent_id": agent_id, "personality_key": "does_not_exist"},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["ok"] is False
        assert "personality" in body["error"].lower()

    def test_update_without_personality_key_succeeds(self, client: TestClient):
        """Updating other fields without touching personality_key should work."""
        created = _create_agent(client, personality_key="software_developer")
        agent_id = created["data"]["agent"]["id"]

        resp = client.post(
            "/api/agents/update",
            json={"agent_id": agent_id, "display_name": "Renamed"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["agent"]["display_name"] == "Renamed"
        # personality_key should remain unchanged
        assert resp.json()["data"]["agent"]["personality_key"] == "software_developer"

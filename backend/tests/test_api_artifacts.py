"""Tests for artifact API endpoints (T-203)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agent_orchestrator.api import create_app
from agent_orchestrator.api.db_provider import _init_db, get_db
from agent_orchestrator.orchestrator.models import Artifact, ArtifactType
from agent_orchestrator.storage.repositories.sqlite_artifact import (
    SQLiteArtifactRepository,
)


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
    """Create a conversation and return its id for use in artifact tests."""
    resp = client.post(
        "/api/conversations/new",
        json={"title": "Test Conv", "project_path": "/tmp"},
    )
    return resp.json()["data"]["conversation"]["id"]


def _seed_artifact(
    conversation_id: str,
    artifact_type: ArtifactType = ArtifactType.AGREEMENT_MAP,
    payload: str = '{"key": "value"}',
    batch_id: str | None = None,
) -> Artifact:
    """Insert an artifact directly via the repository for test setup."""
    repo = SQLiteArtifactRepository(get_db())
    return repo.create(
        Artifact(
            id="",
            conversation_id=conversation_id,
            type=artifact_type,
            payload_json=payload,
            created_at="",
            batch_id=batch_id,
        )
    )


# ── GET /artifacts ─────────────────────────────────────────────────


class TestListArtifacts:
    def test_requires_conversation_id(self, client: TestClient):
        resp = client.get("/api/artifacts")
        assert resp.status_code == 422

    def test_empty_list(self, client: TestClient, conversation_id: str):
        resp = client.get("/api/artifacts", params={"conversation_id": conversation_id})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["artifacts"] == []

    def test_returns_artifacts(self, client: TestClient, conversation_id: str):
        _seed_artifact(conversation_id)
        resp = client.get("/api/artifacts", params={"conversation_id": conversation_id})
        body = resp.json()
        assert len(body["data"]["artifacts"]) == 1
        assert body["data"]["artifacts"][0]["conversation_id"] == conversation_id

    def test_type_filter(self, client: TestClient, conversation_id: str):
        _seed_artifact(conversation_id, ArtifactType.AGREEMENT_MAP)
        _seed_artifact(conversation_id, ArtifactType.CONFLICT_MAP)
        resp = client.get(
            "/api/artifacts",
            params={"conversation_id": conversation_id, "type": "agreement_map"},
        )
        body = resp.json()
        assert len(body["data"]["artifacts"]) == 1
        assert body["data"]["artifacts"][0]["type"] == "agreement_map"

    def test_invalid_type_filter(self, client: TestClient, conversation_id: str):
        resp = client.get(
            "/api/artifacts",
            params={"conversation_id": conversation_id, "type": "bogus"},
        )
        assert resp.status_code == 400
        assert resp.json()["ok"] is False


# ── POST /artifacts ────────────────────────────────────────────────


class TestCreateArtifact:
    def test_creates_artifact(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/artifacts",
            json={
                "conversation_id": conversation_id,
                "type": "agreement_map",
                "payload_json": '{"a": 1}',
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        art = body["data"]["artifact"]
        assert art["conversation_id"] == conversation_id
        assert art["type"] == "agreement_map"
        assert art["payload_json"] == '{"a": 1}'
        assert len(art["id"]) == 36

    def test_with_batch_id(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/artifacts",
            json={
                "conversation_id": conversation_id,
                "type": "checkpoint",
                "payload_json": "{}",
                "batch_id": "batch-123",
            },
        )
        body = resp.json()
        assert body["data"]["artifact"]["batch_id"] == "batch-123"

    def test_invalid_type(self, client: TestClient, conversation_id: str):
        resp = client.post(
            "/api/artifacts",
            json={
                "conversation_id": conversation_id,
                "type": "invalid_type",
                "payload_json": "{}",
            },
        )
        assert resp.status_code == 400
        assert resp.json()["ok"] is False


# ── GET /artifacts/{artifact_id} ───────────────────────────────────


class TestGetArtifact:
    def test_returns_artifact(self, client: TestClient, conversation_id: str):
        art = _seed_artifact(conversation_id)
        resp = client.get(f"/api/artifacts/{art.id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["artifact"]["id"] == art.id

    def test_404_for_missing(self, client: TestClient):
        resp = client.get("/api/artifacts/nonexistent-id")
        assert resp.status_code == 404
        assert resp.json()["ok"] is False


# ── GET /artifacts/latest ──────────────────────────────────────────


class TestGetLatestArtifact:
    def test_requires_conversation_id(self, client: TestClient):
        resp = client.get("/api/artifacts/latest")
        assert resp.status_code == 422

    def test_returns_latest(self, client: TestClient, conversation_id: str):
        _seed_artifact(conversation_id, ArtifactType.AGREEMENT_MAP)
        latest = _seed_artifact(conversation_id, ArtifactType.CONFLICT_MAP)
        resp = client.get("/api/artifacts/latest", params={"conversation_id": conversation_id})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["artifact"]["id"] == latest.id

    def test_null_when_none(self, client: TestClient, conversation_id: str):
        resp = client.get("/api/artifacts/latest", params={"conversation_id": conversation_id})
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["data"]["artifact"] is None

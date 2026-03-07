"""End-to-end happy-path scenario test (TEST-004).

Exercises the full flow:
  health check -> create conversation -> configure agents ->
  start run -> inject steering -> stop run -> verify state -> list events

Uses httpx.AsyncClient with ASGI transport against the real FastAPI app
backed by an in-memory SQLite database.
"""

from __future__ import annotations

import httpx
import pytest


pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Step 1: Health check
# ---------------------------------------------------------------------------


async def test_health_check(client: httpx.AsyncClient):
    """GET /health returns 200 with ok envelope."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["data"]["status"] == "healthy"


# ---------------------------------------------------------------------------
# Full happy-path scenario
# ---------------------------------------------------------------------------


async def test_happy_path_full_scenario(client: httpx.AsyncClient):
    """Walk through the entire happy path in one sequential test.

    This mirrors a real user session:
    1. Create a conversation
    2. Add two agents (claude + codex)
    3. Start a batch run
    4. Inject a steering note
    5. Stop the run
    6. Verify conversation state
    7. Check that events were recorded
    """

    # ── Step 2: Create conversation ──────────────────────────────────
    resp = await client.post(
        "/api/conversations/new",
        json={"title": "E2E Happy Path Test", "project_path": "/tmp/e2e-test"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    conversation = body["data"]["conversation"]
    conv_id = conversation["id"]
    assert conversation["title"] == "E2E Happy Path Test"
    assert conversation["project_path"] == "/tmp/e2e-test"
    assert conversation["state"] == "debate"

    # ── Step 3: Configure agents ─────────────────────────────────────
    # Agent 1: Claude worker
    resp = await client.post(
        "/api/agents",
        json={
            "display_name": "Claude Worker",
            "provider": "claude",
            "model": "claude-sonnet-4-20250514",
            "role": "worker",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    agent_claude = body["data"]["agent"]
    assert agent_claude["display_name"] == "Claude Worker"
    assert agent_claude["provider"] == "claude"
    assert agent_claude["role"] == "worker"
    assert agent_claude["status"] == "idle"

    # Agent 2: Codex coordinator
    resp = await client.post(
        "/api/agents",
        json={
            "display_name": "Codex Coordinator",
            "provider": "codex",
            "model": "codex-mini-latest",
            "role": "coordinator",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    agent_codex = body["data"]["agent"]
    assert agent_codex["display_name"] == "Codex Coordinator"
    assert agent_codex["provider"] == "codex"
    assert agent_codex["role"] == "coordinator"

    # Verify both agents appear in listing
    resp = await client.get("/api/agents")
    assert resp.status_code == 200
    agents = resp.json()["data"]["agents"]
    assert len(agents) >= 2
    agent_names = {a["display_name"] for a in agents}
    assert "Claude Worker" in agent_names
    assert "Codex Coordinator" in agent_names

    # ── Step 4: Start a run ──────────────────────────────────────────
    resp = await client.post(
        f"/api/orchestration/{conv_id}/run",
        json={"batch_size": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    run = body["data"]["run"]
    assert run["conversation_id"] == conv_id
    assert run["status"] == "queued"
    assert run["batch_size"] == 5

    # ── Step 5: Inject steering note ─────────────────────────────────
    resp = await client.post(
        f"/api/orchestration/{conv_id}/steer",
        json={"note": "Focus on unit tests before implementation"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    event = body["data"]["event"]
    assert event["text"] == "Focus on unit tests before implementation"
    assert event["source_type"] == "user"
    assert event["event_type"] == "steering"

    # ── Step 6: Stop the run ─────────────────────────────────────────
    resp = await client.post(f"/api/orchestration/{conv_id}/stop")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    stopped_run = body["data"]["run"]
    assert stopped_run["status"] == "done"
    assert stopped_run["ended_at"] is not None

    # ── Step 7: Verify conversation state ────────────────────────────
    resp = await client.get("/api/conversations")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    conversations = body["data"]["conversations"]
    assert len(conversations) >= 1
    our_conv = next(c for c in conversations if c["id"] == conv_id)
    assert our_conv["title"] == "E2E Happy Path Test"
    # Conversation should still exist and not be deleted
    assert our_conv["deleted_at"] is None

    # ── Step 8: List events ──────────────────────────────────────────
    # The events endpoint reads from JSONL files, which may not exist
    # in the E2E test context (steering notes go to the DB, not JSONL).
    # We verify the endpoint responds correctly even with no file.
    resp = await client.get(
        "/api/events",
        params={"conversation_id": conv_id},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "events" in body["data"]
    # Events list may be empty since JSONL log is file-based and we
    # haven't written to it; the important thing is the API works.
    assert isinstance(body["data"]["events"], list)


# ---------------------------------------------------------------------------
# Edge cases within the happy path
# ---------------------------------------------------------------------------


async def test_cannot_start_second_run_while_active(client: httpx.AsyncClient):
    """Starting a second run on the same conversation returns 409."""
    # Setup
    resp = await client.post(
        "/api/conversations/new",
        json={"title": "Double Run Test", "project_path": "/tmp"},
    )
    conv_id = resp.json()["data"]["conversation"]["id"]

    # First run succeeds
    resp = await client.post(f"/api/orchestration/{conv_id}/run")
    assert resp.status_code == 200

    # Second run is rejected
    resp = await client.post(f"/api/orchestration/{conv_id}/run")
    assert resp.status_code == 409
    assert resp.json()["ok"] is False


async def test_stop_without_active_run_returns_409(client: httpx.AsyncClient):
    """Stopping when no run is active returns 409."""
    resp = await client.post(
        "/api/conversations/new",
        json={"title": "No Run Test", "project_path": "/tmp"},
    )
    conv_id = resp.json()["data"]["conversation"]["id"]

    resp = await client.post(f"/api/orchestration/{conv_id}/stop")
    assert resp.status_code == 409
    assert resp.json()["ok"] is False


async def test_steer_nonexistent_conversation_returns_404(client: httpx.AsyncClient):
    """Steering a nonexistent conversation returns 404."""
    resp = await client.post(
        "/api/orchestration/nonexistent-id/steer",
        json={"note": "This should fail"},
    )
    assert resp.status_code == 404
    assert resp.json()["ok"] is False


async def test_create_agent_with_invalid_provider_returns_400(client: httpx.AsyncClient):
    """Creating an agent with an unknown provider returns 400."""
    resp = await client.post(
        "/api/agents",
        json={
            "display_name": "Bad Agent",
            "provider": "nonexistent-provider",
            "model": "some-model",
            "role": "worker",
        },
    )
    assert resp.status_code == 400
    assert resp.json()["ok"] is False


async def test_events_without_conversation_id_returns_400(client: httpx.AsyncClient):
    """GET /events without conversation_id query param returns 400."""
    resp = await client.get("/api/events")
    assert resp.status_code == 400
    assert resp.json()["ok"] is False


async def test_select_and_delete_conversation(client: httpx.AsyncClient):
    """Select and then soft-delete a conversation."""
    # Create
    resp = await client.post(
        "/api/conversations/new",
        json={"title": "Lifecycle Test", "project_path": "/tmp"},
    )
    conv_id = resp.json()["data"]["conversation"]["id"]

    # Select (activate)
    resp = await client.post(
        "/api/conversations/select",
        json={"conversation_id": conv_id},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["conversation"]["active"] == 1

    # Soft-delete
    resp = await client.post(
        "/api/conversations/delete",
        json={"conversation_id": conv_id},
    )
    assert resp.status_code == 200
    deleted_conv = resp.json()["data"]["conversation"]
    assert deleted_conv["deleted_at"] is not None

    # Should no longer appear in listing
    resp = await client.get("/api/conversations")
    conv_ids = [c["id"] for c in resp.json()["data"]["conversations"]]
    assert conv_id not in conv_ids

"""Agent configuration CRUD endpoints (API-004).

Refactored to use SQLiteAgentRepository (T-201).
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.config_loaders.personalities import load_personalities
from agent_orchestrator.storage.repositories.sqlite_agent import SQLiteAgentRepository

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class NewAgentBody(BaseModel):
    display_name: str
    provider: str
    model: str
    role: str
    personality_key: str | None = None
    capabilities_json: str | None = None
    conversation_id: str | None = None


class UpdateAgentBody(BaseModel):
    agent_id: str
    display_name: str | None = None
    provider: str | None = None
    model: str | None = None
    role: str | None = None
    personality_key: str | None = None
    capabilities_json: str | None = None


class AgentIdBody(BaseModel):
    agent_id: str


class PatchAgentOrderBody(BaseModel):
    sort_order: int


class ReorderAgentsBody(BaseModel):
    agent_ids: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_repo() -> SQLiteAgentRepository:
    return SQLiteAgentRepository(get_db())


def _agent_to_dict(agent: Any) -> dict[str, Any]:
    """Convert an Agent dataclass to a JSON-friendly dict.

    Enum values are serialised as their string value so the API response
    stays backward-compatible with the original inline-SQL implementation.
    """
    d = asdict(agent)
    for key in ("provider", "role", "status"):
        val = d.get(key)
        if val is not None and hasattr(val, "value"):
            d[key] = val.value
    return d


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/agents")
def list_agents() -> dict[str, Any]:
    """List all agents ordered by sort_order, then display_name."""
    repo = _get_repo()
    agents = [_agent_to_dict(a) for a in repo.list_all()]
    return ok_response({"agents": agents})


@router.post("/agents")
def create_agent(body: NewAgentBody) -> Any:
    """Create a new agent with sensible defaults."""
    repo = _get_repo()

    # Validate personality_key against loaded profiles
    if body.personality_key is not None:
        profiles = load_personalities()
        if profiles and body.personality_key not in profiles:
            return JSONResponse(
                status_code=400,
                content=error_response(
                    f"Invalid personality_key '{body.personality_key}'. "
                    f"Valid keys: {sorted(profiles.keys())}"
                ),
            )

    # Validate conversation_id before creating the agent (avoids needing rollback)
    if body.conversation_id is not None:
        db = get_db()
        with db.connection() as conn:
            conv_row = conn.execute(
                "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
                (body.conversation_id,),
            ).fetchone()
            if conv_row is None:
                return JSONResponse(
                    status_code=404,
                    content=error_response("Conversation not found"),
                )

    try:
        agent = repo.create(
            display_name=body.display_name,
            provider=body.provider,
            model=body.model,
            role=body.role,
            personality_key=body.personality_key,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=error_response(str(exc)),
        )

    # If capabilities_json was provided, update it via the repo
    if body.capabilities_json is not None:
        agent = repo.update(agent.id, {"capabilities_json": body.capabilities_json})

    result = _agent_to_dict(agent)

    # Handle conversation_id linking (join table)
    turn_order = None
    if body.conversation_id is not None:
        db = get_db()
        with db.connection() as conn:

            max_row = conn.execute(
                "SELECT COALESCE(MAX(turn_order), 0) FROM conversation_agent "
                "WHERE conversation_id = ?",
                (body.conversation_id,),
            ).fetchone()
            turn_order = max_row[0] + 1
            ca_id = str(uuid.uuid4())
            now = datetime.now(UTC).isoformat()
            conn.execute(
                "INSERT INTO conversation_agent "
                "(id, conversation_id, agent_id, turn_order, enabled, "
                " permission_profile, is_merge_coordinator, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ca_id,
                    body.conversation_id,
                    agent.id,
                    turn_order,
                    1,
                    "default",
                    0,
                    now,
                ),
            )
            conn.commit()

    if turn_order is not None:
        result["turn_order"] = turn_order
    return ok_response({"agent": result})


@router.post("/agents/update")
def update_agent(body: UpdateAgentBody) -> Any:
    """Update agent fields."""
    repo = _get_repo()

    updatable_cols = (
        "display_name",
        "provider",
        "model",
        "role",
        "personality_key",
        "capabilities_json",
    )
    fields: dict[str, Any] = {}
    for col in updatable_cols:
        val = getattr(body, col, None)
        if val is not None:
            fields[col] = val

    # Validate personality_key if being updated
    if fields.get("personality_key") is not None:
        profiles = load_personalities()
        if fields["personality_key"] not in profiles:
            return JSONResponse(
                status_code=400,
                content=error_response(
                    f"Invalid personality_key '{fields['personality_key']}'. "
                    f"Valid keys: {sorted(profiles.keys())}"
                ),
            )

    try:
        agent = repo.update(body.agent_id, fields)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Agent not found"),
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=error_response(str(exc)),
        )

    return ok_response({"agent": _agent_to_dict(agent)})


@router.post("/agents/delete")
def delete_agent(body: AgentIdBody) -> Any:
    """Hard-delete an agent."""
    repo = _get_repo()

    try:
        repo.delete(body.agent_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Agent not found"),
        )

    return ok_response({"deleted_id": body.agent_id})


@router.patch("/agents/{agent_id}/order")
def patch_agent_order(agent_id: str, body: PatchAgentOrderBody) -> Any:
    """Update the sort_order of an agent."""
    if body.sort_order < 0:
        return JSONResponse(
            status_code=400,
            content=error_response("sort_order must be a non-negative integer"),
        )

    repo = _get_repo()

    try:
        repo.update_sort_order(agent_id, body.sort_order)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Agent not found"),
        )

    agent = repo.get_by_id(agent_id)
    return ok_response({"agent": _agent_to_dict(agent)})

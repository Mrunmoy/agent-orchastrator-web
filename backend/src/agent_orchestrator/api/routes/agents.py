"""Agent configuration CRUD endpoints (API-004)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.orchestrator.models import AgentRole, Provider

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

VALID_PROVIDERS = {p.value for p in Provider}
VALID_ROLES = {r.value for r in AgentRole}


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

_AGENT_KEYS = [
    "id",
    "display_name",
    "provider",
    "model",
    "personality_key",
    "role",
    "status",
    "session_id",
    "capabilities_json",
    "sort_order",
    "created_at",
    "updated_at",
]


def _row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(_AGENT_KEYS, row))


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/agents")
def list_agents() -> dict[str, Any]:
    """List all agents ordered by sort_order, then display_name."""
    db = get_db()
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT * FROM agent ORDER BY sort_order ASC, display_name ASC"
        ).fetchall()
    agents = [_row_to_dict(r) for r in rows]
    return ok_response({"agents": agents})


@router.post("/agents")
def create_agent(body: NewAgentBody) -> Any:
    """Create a new agent with sensible defaults."""
    # Validate provider
    if body.provider not in VALID_PROVIDERS:
        return JSONResponse(
            status_code=400,
            content=error_response(
                f"Invalid provider '{body.provider}'. "
                f"Valid providers: {sorted(VALID_PROVIDERS)}"
            ),
        )
    # Validate role
    if body.role not in VALID_ROLES:
        return JSONResponse(
            status_code=400,
            content=error_response(
                f"Invalid role '{body.role}'. " f"Valid roles: {sorted(VALID_ROLES)}"
            ),
        )

    now = datetime.now(UTC).isoformat()
    agent_id = str(uuid.uuid4())
    capabilities = body.capabilities_json or "[]"

    db = get_db()
    with db.connection() as conn:
        # Validate conversation_id if provided
        if body.conversation_id is not None:
            conv_row = conn.execute(
                "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
                (body.conversation_id,),
            ).fetchone()
            if conv_row is None:
                return JSONResponse(
                    status_code=404,
                    content=error_response("Conversation not found"),
                )

        conn.execute(
            "INSERT INTO agent "
            "(id, display_name, provider, model, personality_key, role, "
            " status, session_id, capabilities_json, sort_order, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                agent_id,
                body.display_name,
                body.provider,
                body.model,
                body.personality_key,
                body.role,
                "idle",
                None,
                capabilities,
                0,
                now,
                now,
            ),
        )

        turn_order = None
        if body.conversation_id is not None:
            # Get max turn_order for this conversation
            max_row = conn.execute(
                "SELECT COALESCE(MAX(turn_order), 0) FROM conversation_agent "
                "WHERE conversation_id = ?",
                (body.conversation_id,),
            ).fetchone()
            turn_order = max_row[0] + 1
            ca_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO conversation_agent "
                "(id, conversation_id, agent_id, turn_order, enabled, "
                " permission_profile, is_merge_coordinator, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    ca_id,
                    body.conversation_id,
                    agent_id,
                    turn_order,
                    1,
                    "default",
                    0,
                    now,
                ),
            )

        conn.commit()
        row = conn.execute("SELECT * FROM agent WHERE id = ?", (agent_id,)).fetchone()

    agent = _row_to_dict(row)
    if turn_order is not None:
        agent["turn_order"] = turn_order
    return ok_response({"agent": agent})


@router.post("/agents/update")
def update_agent(body: UpdateAgentBody) -> Any:
    """Update agent fields."""
    db = get_db()
    with db.connection() as conn:
        row = conn.execute(
            "SELECT id FROM agent WHERE id = ?",
            (body.agent_id,),
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404,
                content=error_response("Agent not found"),
            )

        # Build SET clause from provided fields
        updatable = {
            "display_name": body.display_name,
            "provider": body.provider,
            "model": body.model,
            "role": body.role,
            "personality_key": body.personality_key,
            "capabilities_json": body.capabilities_json,
        }
        sets: list[str] = []
        vals: list[Any] = []
        for col, val in updatable.items():
            if val is not None:
                sets.append(f"{col} = ?")
                vals.append(val)

        # Validate provider if being updated
        if body.provider is not None and body.provider not in VALID_PROVIDERS:
            return JSONResponse(
                status_code=400,
                content=error_response(
                    f"Invalid provider '{body.provider}'. "
                    f"Valid providers: {sorted(VALID_PROVIDERS)}"
                ),
            )
        # Validate role if being updated
        if body.role is not None and body.role not in VALID_ROLES:
            return JSONResponse(
                status_code=400,
                content=error_response(
                    f"Invalid role '{body.role}'. " f"Valid roles: {sorted(VALID_ROLES)}"
                ),
            )

        if sets:
            now = datetime.now(UTC).isoformat()
            sets.append("updated_at = ?")
            vals.append(now)
            vals.append(body.agent_id)
            conn.execute(
                f"UPDATE agent SET {', '.join(sets)} WHERE id = ?",  # noqa: S608
                vals,
            )
            conn.commit()

        updated = conn.execute(
            "SELECT * FROM agent WHERE id = ?",
            (body.agent_id,),
        ).fetchone()
    return ok_response({"agent": _row_to_dict(updated)})


@router.post("/agents/delete")
def delete_agent(body: AgentIdBody) -> Any:
    """Hard-delete an agent."""
    db = get_db()
    with db.connection() as conn:
        row = conn.execute(
            "SELECT id FROM agent WHERE id = ?",
            (body.agent_id,),
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404,
                content=error_response("Agent not found"),
            )
        conn.execute("DELETE FROM conversation_agent WHERE agent_id = ?", (body.agent_id,))
        conn.execute("DELETE FROM agent WHERE id = ?", (body.agent_id,))
        conn.commit()
    return ok_response({"deleted_id": body.agent_id})


@router.patch("/agents/{agent_id}/order")
def patch_agent_order(agent_id: str, body: PatchAgentOrderBody) -> Any:
    """Update the sort_order of an agent."""
    if body.sort_order < 0:
        return JSONResponse(
            status_code=400,
            content=error_response("sort_order must be a non-negative integer"),
        )
    db = get_db()
    with db.connection() as conn:
        row = conn.execute(
            "SELECT id FROM agent WHERE id = ?",
            (agent_id,),
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404,
                content=error_response("Agent not found"),
            )
        now = datetime.now(UTC).isoformat()
        conn.execute(
            "UPDATE agent SET sort_order = ?, updated_at = ? WHERE id = ?",
            (body.sort_order, now, agent_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM agent WHERE id = ?",
            (agent_id,),
        ).fetchone()
    return ok_response({"agent": _row_to_dict(updated)})

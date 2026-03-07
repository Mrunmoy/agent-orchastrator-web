"""Agent configuration CRUD endpoints (API-004)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.orchestrator.models import AgentRole, Provider
from agent_orchestrator.storage import DatabaseManager

# ---------------------------------------------------------------------------
# Module-level database (in-memory for now; replace with DI later)
# ---------------------------------------------------------------------------

_db: DatabaseManager | None = None


def _init_db() -> None:
    """(Re)initialise the module-level in-memory database."""
    global _db  # noqa: PLW0603
    if _db is not None:
        _db.close()
    _db = DatabaseManager(":memory:", check_same_thread=False)
    _db.initialize()


def get_db() -> DatabaseManager:
    """Return the module-level DatabaseManager, initialising if needed."""
    global _db  # noqa: PLW0603
    if _db is None:
        _init_db()
    assert _db is not None
    return _db


# Eagerly initialise on import so the router works immediately.
_init_db()

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
    """List all agents ordered by display_name."""
    db = get_db()
    with db.connection() as conn:
        rows = conn.execute(
            "SELECT * FROM agent ORDER BY display_name"
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
                f"Invalid role '{body.role}'. "
                f"Valid roles: {sorted(VALID_ROLES)}"
            ),
        )

    now = datetime.now(UTC).isoformat()
    agent_id = str(uuid.uuid4())
    capabilities = body.capabilities_json or "[]"

    db = get_db()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO agent "
            "(id, display_name, provider, model, personality_key, role, "
            " status, session_id, capabilities_json, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM agent WHERE id = ?", (agent_id,)).fetchone()
    return ok_response({"agent": _row_to_dict(row)})


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
                    f"Invalid role '{body.role}'. "
                    f"Valid roles: {sorted(VALID_ROLES)}"
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
        conn.execute("DELETE FROM agent WHERE id = ?", (body.agent_id,))
        conn.commit()
    return ok_response({"deleted_id": body.agent_id})

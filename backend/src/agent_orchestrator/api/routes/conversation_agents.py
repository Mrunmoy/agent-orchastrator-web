"""Conversation-scoped agent endpoints (UI-014)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class ReorderBody(BaseModel):
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


def _conversation_exists(conn, conversation_id: str) -> bool:
    row = conn.execute(
        "SELECT id FROM conversation WHERE id = ? AND deleted_at IS NULL",
        (conversation_id,),
    ).fetchone()
    return row is not None


def _get_conversation_agents(conn, conversation_id: str) -> list[dict[str, Any]]:
    """Return agents for a conversation joined with conversation_agent, ordered by turn_order."""
    rows = conn.execute(
        "SELECT a.*, ca.turn_order "
        "FROM agent a "
        "JOIN conversation_agent ca ON a.id = ca.agent_id "
        "WHERE ca.conversation_id = ? AND ca.enabled = 1 "
        "ORDER BY ca.turn_order ASC",
        (conversation_id,),
    ).fetchall()
    agents = []
    for row in rows:
        d = dict(zip(_AGENT_KEYS, row[: len(_AGENT_KEYS)]))
        d["turn_order"] = row[len(_AGENT_KEYS)]
        agents.append(d)
    return agents


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/conversations/{conversation_id}/agents")
def list_conversation_agents(conversation_id: str) -> Any:
    """List agents assigned to a conversation, ordered by turn_order."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
        agents = _get_conversation_agents(conn, conversation_id)
    return ok_response({"agents": agents})


@router.post("/conversations/{conversation_id}/agents/{agent_id}/remove")
def remove_agent_from_conversation(conversation_id: str, agent_id: str) -> Any:
    """Remove an agent from a conversation (deletes the join row, not the agent)."""
    db = get_db()
    with db.connection() as conn:
        row = conn.execute(
            "SELECT id FROM conversation_agent " "WHERE conversation_id = ? AND agent_id = ?",
            (conversation_id, agent_id),
        ).fetchone()
        if row is None:
            return JSONResponse(
                status_code=404,
                content=error_response("Agent not linked to this conversation"),
            )
        conn.execute(
            "DELETE FROM conversation_agent " "WHERE conversation_id = ? AND agent_id = ?",
            (conversation_id, agent_id),
        )
        conn.commit()
    return ok_response({"removed_agent_id": agent_id})


@router.patch("/conversations/{conversation_id}/agents/reorder")
def reorder_conversation_agents(conversation_id: str, body: ReorderBody) -> Any:
    """Reorder agents in a conversation by specifying the desired agent_ids order."""
    db = get_db()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
        # Get current agent ids for this conversation
        rows = conn.execute(
            "SELECT agent_id FROM conversation_agent " "WHERE conversation_id = ? AND enabled = 1",
            (conversation_id,),
        ).fetchall()
        current_ids = {r[0] for r in rows}
        requested_ids = set(body.agent_ids)

        if current_ids != requested_ids:
            return JSONResponse(
                status_code=400,
                content=error_response(
                    "agent_ids must exactly match the conversation's current agents"
                ),
            )

        # Update turn_order for each agent (1-based)
        for idx, agent_id in enumerate(body.agent_ids, start=1):
            conn.execute(
                "UPDATE conversation_agent SET turn_order = ? "
                "WHERE conversation_id = ? AND agent_id = ?",
                (idx, conversation_id, agent_id),
            )
        conn.commit()

        agents = _get_conversation_agents(conn, conversation_id)
    return ok_response({"agents": agents})

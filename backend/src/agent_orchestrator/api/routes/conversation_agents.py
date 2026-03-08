"""Conversation-scoped agent endpoints (UI-014, T-106)."""

from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.storage.repositories.sqlite_conversation_agent import (
    SQLiteConversationAgentRepository,
)

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class AddAgentBody(BaseModel):
    agent_id: str
    permission_profile: str = "default"


class ReorderBody(BaseModel):
    agent_ids: list[str]


class MergeCoordinatorBody(BaseModel):
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


def _get_repo() -> SQLiteConversationAgentRepository:
    return SQLiteConversationAgentRepository(get_db())


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


@router.post("/conversations/{conversation_id}/agents")
def add_agent_to_conversation(conversation_id: str, body: AddAgentBody) -> Any:
    """Add an agent to a conversation with auto-assigned turn_order."""
    db = get_db()
    repo = _get_repo()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
    try:
        record = repo.add_agent_to_conversation(
            conversation_id, body.agent_id, body.permission_profile
        )
    except sqlite3.IntegrityError:
        return JSONResponse(
            status_code=409,
            content=error_response("Agent already assigned to this conversation"),
        )
    return ok_response(record)


@router.delete("/conversations/{conversation_id}/agents/{agent_id}")
def remove_agent_from_conversation(conversation_id: str, agent_id: str) -> Any:
    """Remove an agent from a conversation (deletes the join row, not the agent)."""
    repo = _get_repo()
    try:
        repo.remove_agent(conversation_id, agent_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Agent not linked to this conversation"),
        )
    return ok_response({"removed_agent_id": agent_id})


@router.patch("/conversations/{conversation_id}/agents/reorder")
def reorder_conversation_agents(conversation_id: str, body: ReorderBody) -> Any:
    """Reorder agents in a conversation by specifying the desired agent_ids order."""
    db = get_db()
    repo = _get_repo()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
    try:
        repo.reorder(conversation_id, body.agent_ids)
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=error_response(str(exc)),
        )

    with db.connection() as conn:
        agents = _get_conversation_agents(conn, conversation_id)
    return ok_response({"agents": agents})


@router.patch("/conversations/{conversation_id}/agents/merge-coordinator")
def set_merge_coordinator(conversation_id: str, body: MergeCoordinatorBody) -> Any:
    """Set the merge coordinator for a conversation."""
    db = get_db()
    repo = _get_repo()
    with db.connection() as conn:
        if not _conversation_exists(conn, conversation_id):
            return JSONResponse(
                status_code=404,
                content=error_response("Conversation not found"),
            )
    try:
        repo.set_merge_coordinator(conversation_id, body.agent_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Agent not linked to this conversation"),
        )
    return ok_response({"merge_coordinator": body.agent_id})

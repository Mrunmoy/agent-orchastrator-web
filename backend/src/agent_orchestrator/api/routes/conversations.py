"""Conversation CRUD endpoints (API-002).

Refactored to use SQLiteConversationRepository (T-104).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.storage.repositories.sqlite_conversation import (
    SQLiteConversationRepository,
)

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class NewConversationBody(BaseModel):
    title: str
    project_path: str


class ConversationIdBody(BaseModel):
    conversation_id: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_repo() -> SQLiteConversationRepository:
    return SQLiteConversationRepository(get_db())


def _conv_to_dict(conv: Any) -> dict[str, Any]:
    """Convert a Conversation dataclass to a JSON-friendly dict.

    Enum values are serialised as their string value so the API response
    stays backward-compatible with the original inline-SQL implementation.
    """
    d = asdict(conv)
    # Enum fields need .value for JSON serialisation
    for key in ("state", "phase", "gate_status"):
        val = d.get(key)
        if val is not None and hasattr(val, "value"):
            d[key] = val.value
    return d


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/conversations")
def list_conversations() -> dict[str, Any]:
    """List all non-deleted conversations ordered by updated_at DESC."""
    repo = _get_repo()
    conversations = [_conv_to_dict(c) for c in repo.list_active()]
    return ok_response({"conversations": conversations})


@router.post("/conversations/new")
def create_conversation(body: NewConversationBody) -> dict[str, Any]:
    """Create a new conversation with sensible defaults."""
    repo = _get_repo()
    conv = repo.create(body.title, body.project_path)
    return ok_response({"conversation": _conv_to_dict(conv)})


@router.post("/conversations/select")
def select_conversation(body: ConversationIdBody) -> Any:
    """Set one conversation as active, deactivating all others."""
    repo = _get_repo()
    conv = repo.select(body.conversation_id)
    if conv is None:
        return JSONResponse(
            status_code=404,
            content=error_response("Conversation not found"),
        )
    return ok_response({"conversation": _conv_to_dict(conv)})


@router.post("/conversations/delete")
def delete_conversation(body: ConversationIdBody) -> Any:
    """Soft-delete a conversation by setting deleted_at."""
    repo = _get_repo()
    conv = repo.soft_delete(body.conversation_id)
    if conv is None:
        return JSONResponse(
            status_code=404,
            content=error_response("Conversation not found"),
        )
    return ok_response({"conversation": _conv_to_dict(conv)})


@router.post("/conversations/clear-all")
def clear_all_conversations() -> dict[str, Any]:
    """Soft-delete all non-deleted conversations. Return count."""
    repo = _get_repo()
    count = repo.clear_all()
    return ok_response({"deleted_count": count})

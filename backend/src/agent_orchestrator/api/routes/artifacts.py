"""Artifact CRUD endpoints (T-203).

Exposes endpoints for creating and querying structured artifacts
(agreement maps, conflict maps, checkpoints, etc.) produced during
orchestration.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.orchestrator.models import Artifact, ArtifactType
from agent_orchestrator.storage.repositories.sqlite_artifact import (
    SQLiteArtifactRepository,
)

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class NewArtifactBody(BaseModel):
    conversation_id: str
    type: str
    payload_json: str
    batch_id: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_repo() -> SQLiteArtifactRepository:
    return SQLiteArtifactRepository(get_db())


def _artifact_to_dict(art: Artifact) -> dict[str, Any]:
    """Convert an Artifact dataclass to a JSON-friendly dict."""
    d = asdict(art)
    # Enum fields need .value for JSON serialisation
    if hasattr(d.get("type"), "value"):
        d["type"] = d["type"].value
    return d


def _parse_artifact_type(raw: str) -> ArtifactType | None:
    """Try to parse a string into an ArtifactType, returning None on failure."""
    try:
        return ArtifactType(raw)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/artifacts/latest")
def get_latest_artifact(
    conversation_id: str = Query(...),
) -> dict[str, Any]:
    """Return the most recent artifact for a conversation."""
    repo = _get_repo()
    art = repo.get_latest(conversation_id)
    return ok_response({"artifact": _artifact_to_dict(art) if art else None})


@router.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str) -> Any:
    """Return a single artifact by id."""
    repo = _get_repo()
    art = repo.get_by_id(artifact_id)
    if art is None:
        return JSONResponse(
            status_code=404,
            content=error_response("Artifact not found"),
        )
    return ok_response({"artifact": _artifact_to_dict(art)})


@router.get("/artifacts")
def list_artifacts(
    conversation_id: str = Query(...),
    type: str | None = Query(default=None),
) -> Any:
    """List artifacts for a conversation, with optional type filter."""
    repo = _get_repo()
    type_filter: ArtifactType | None = None
    if type is not None:
        type_filter = _parse_artifact_type(type)
        if type_filter is None:
            return JSONResponse(
                status_code=400,
                content=error_response(f"Invalid artifact type: {type}"),
            )
    artifacts = [
        _artifact_to_dict(a)
        for a in repo.list_by_conversation(conversation_id, type_filter=type_filter)
    ]
    return ok_response({"artifacts": artifacts})


@router.post("/artifacts")
def create_artifact(body: NewArtifactBody) -> Any:
    """Create a new artifact."""
    art_type = _parse_artifact_type(body.type)
    if art_type is None:
        return JSONResponse(
            status_code=400,
            content=error_response(f"Invalid artifact type: {body.type}"),
        )
    repo = _get_repo()
    artifact = repo.create(
        Artifact(
            id="",
            conversation_id=body.conversation_id,
            type=art_type,
            payload_json=body.payload_json,
            created_at="",
            batch_id=body.batch_id,
        )
    )
    return ok_response({"artifact": _artifact_to_dict(artifact)})

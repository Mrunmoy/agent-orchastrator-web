"""Task CRUD endpoints (T-202).

Provides list, create, get, and partial-update operations for tasks
scoped to a conversation.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_orchestrator.api.db_provider import get_db
from agent_orchestrator.api.responses import error_response, ok_response
from agent_orchestrator.orchestrator.models import TaskStatus
from agent_orchestrator.storage.repositories.sqlite_task import SQLiteTaskRepository

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class NewTaskBody(BaseModel):
    conversation_id: str
    title: str
    spec_json: str
    priority: int = 100
    depends_on: list[str] | None = None


class UpdateStatusBody(BaseModel):
    status: str


class AssignOwnerBody(BaseModel):
    agent_id: str


class UpdateResultBody(BaseModel):
    result_summary: str
    evidence_json: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_repo() -> SQLiteTaskRepository:
    return SQLiteTaskRepository(get_db())


def _task_to_dict(task: Any) -> dict[str, Any]:
    """Convert a Task dataclass to a JSON-friendly dict."""
    d = asdict(task)
    for key in ("status",):
        val = d.get(key)
        if val is not None and hasattr(val, "value"):
            d[key] = val.value
    return d


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.get("/tasks")
def list_tasks(
    conversation_id: str = Query(...),
    status: str | None = Query(None),
) -> Any:
    """List tasks for a conversation, optionally filtered by status."""
    repo = _get_repo()

    status_filter: TaskStatus | None = None
    if status is not None:
        try:
            status_filter = TaskStatus(status)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content=error_response(f"Invalid status: {status!r}"),
            )

    tasks = repo.list_by_conversation(conversation_id, status_filter=status_filter)
    return ok_response({"tasks": [_task_to_dict(t) for t in tasks]})


@router.post("/tasks")
def create_task(body: NewTaskBody) -> dict[str, Any]:
    """Create a new task within a conversation."""
    repo = _get_repo()
    task = repo.create(
        body.conversation_id,
        body.title,
        body.spec_json,
        priority=body.priority,
        depends_on=body.depends_on,
    )
    return ok_response({"task": _task_to_dict(task)})


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> Any:
    """Get a single task by id."""
    repo = _get_repo()
    task = repo.get_by_id(task_id)
    if task is None:
        return JSONResponse(
            status_code=404,
            content=error_response("Task not found"),
        )
    return ok_response({"task": _task_to_dict(task)})


@router.patch("/tasks/{task_id}/status")
def update_task_status(task_id: str, body: UpdateStatusBody) -> Any:
    """Update the status of a task."""
    repo = _get_repo()

    try:
        new_status = TaskStatus(body.status)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content=error_response(f"Invalid status: {body.status!r}"),
        )

    try:
        repo.update_status(task_id, new_status)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Task not found"),
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content=error_response(str(exc)),
        )

    return ok_response({"updated": True})


@router.patch("/tasks/{task_id}/owner")
def assign_task_owner(task_id: str, body: AssignOwnerBody) -> Any:
    """Assign an owner agent to a task."""
    repo = _get_repo()
    try:
        repo.assign_owner(task_id, body.agent_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Task not found"),
        )
    except sqlite3.IntegrityError:
        return JSONResponse(
            status_code=400,
            content=error_response(f"Invalid agent_id: {body.agent_id!r}"),
        )
    return ok_response({"updated": True})


@router.patch("/tasks/{task_id}/result")
def update_task_result(task_id: str, body: UpdateResultBody) -> Any:
    """Update the result summary and evidence for a task."""
    repo = _get_repo()
    try:
        repo.update_result(task_id, body.result_summary, body.evidence_json)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content=error_response("Task not found"),
        )
    return ok_response({"updated": True})

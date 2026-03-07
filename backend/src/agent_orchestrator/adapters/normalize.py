"""Adapter output normalization to a common message schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus

_STATUS_MAP: dict[AdapterStatus, str] = {
    AdapterStatus.IDLE: "ok",
    AdapterStatus.RUNNING: "ok",
    AdapterStatus.TIMED_OUT: "timeout",
    AdapterStatus.ERROR: "error",
}


@dataclass
class NormalizedMessage:
    """Common message schema produced by normalizing adapter output."""

    agent_id: str
    text: str
    timestamp: str  # ISO-8601 UTC
    status: str  # "ok", "timeout", "error"
    session_id: str | None = None
    token_count: int | None = None  # estimated
    metadata: dict = field(default_factory=dict)


def normalize(
    result: AdapterResult,
    *,
    agent_id: str,
    timestamp: str | None = None,
) -> NormalizedMessage:
    """Normalize an AdapterResult into a NormalizedMessage."""
    text = result.text.strip()
    return NormalizedMessage(
        agent_id=agent_id,
        text=text,
        timestamp=timestamp or datetime.now(UTC).isoformat(),
        status=_STATUS_MAP[result.status],
        session_id=result.session_id,
        token_count=len(text.split()),
        metadata=result.metadata,
    )


def normalize_batch(
    results: list[tuple[str, AdapterResult]],
    *,
    timestamp: str | None = None,
) -> list[NormalizedMessage]:
    """Normalize a batch of (agent_id, AdapterResult) pairs."""
    return [
        normalize(result, agent_id=agent_id, timestamp=timestamp)
        for agent_id, result in results
    ]

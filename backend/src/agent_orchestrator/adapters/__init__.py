"""CLI agent adapters: Claude, Codex, Ollama."""

from agent_orchestrator.adapters.normalize import (
    NormalizedMessage,
    normalize,
    normalize_batch,
)

__all__ = [
    "NormalizedMessage",
    "normalize",
    "normalize_batch",
]

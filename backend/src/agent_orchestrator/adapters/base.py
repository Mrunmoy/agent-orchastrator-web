"""Base adapter interface for CLI agents."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum


class AdapterStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    TIMED_OUT = "timed_out"
    ERROR = "error"


@dataclass
class AdapterResult:
    """Result from an adapter invocation."""

    text: str
    session_id: str | None = None
    status: AdapterStatus = AdapterStatus.IDLE
    metadata: dict = field(default_factory=dict)


class BaseAdapter(abc.ABC):
    """Abstract base for CLI agent adapters."""

    @abc.abstractmethod
    async def send_prompt(
        self,
        prompt: str,
        *,
        working_dir: str,
        session_id: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> AdapterResult:
        """Send a prompt to the CLI agent and return the result."""

    @abc.abstractmethod
    async def resume_session(
        self,
        session_id: str,
        prompt: str,
        *,
        working_dir: str,
        timeout_seconds: float = 120.0,
    ) -> AdapterResult:
        """Resume an existing session with a new prompt."""

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if the CLI tool is available on the system."""

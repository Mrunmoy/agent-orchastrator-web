"""Capacity-aware throttle and run queue (ORCH-006).

Decides whether new agent runs may start based on system resource usage and
the number of currently active runs.  Provides a FIFO queue for runs that
must wait until capacity is available.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Policy & decision data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThrottlePolicy:
    """Configurable thresholds for the capacity throttle."""

    max_concurrent_runs: int = 3
    max_cpu_percent: float = 85.0
    max_memory_percent: float = 90.0


@dataclass(frozen=True)
class ThrottleDecision:
    """Result of a throttle evaluation."""

    allowed: bool
    reason: str
    current_runs: int
    cpu_percent: float
    memory_percent: float


# ---------------------------------------------------------------------------
# CapacityThrottle
# ---------------------------------------------------------------------------


class CapacityThrottle:
    """Tracks active runs and evaluates whether a new run is allowed."""

    def __init__(self, policy: ThrottlePolicy | None = None) -> None:
        self._policy = policy or ThrottlePolicy()
        # OrderedDict used as an ordered set for deterministic iteration
        self._active: OrderedDict[str, None] = OrderedDict()

    # -- run tracking ------------------------------------------------------

    def register_run(self, conversation_id: str) -> None:
        """Track *conversation_id* as an active run (idempotent)."""
        self._active[conversation_id] = None

    def release_run(self, conversation_id: str) -> None:
        """Remove *conversation_id* from active tracking (no-op if absent)."""
        self._active.pop(conversation_id, None)

    def active_runs(self) -> list[str]:
        """Return the list of active conversation IDs."""
        return list(self._active)

    # -- capacity check ----------------------------------------------------

    def check(self, cpu_percent: float, memory_percent: float) -> ThrottleDecision:
        """Evaluate whether a new run is allowed given current metrics."""
        current = len(self._active)

        if current >= self._policy.max_concurrent_runs:
            return ThrottleDecision(
                allowed=False,
                reason=(
                    f"Active concurrent runs ({current}) "
                    f">= max ({self._policy.max_concurrent_runs})"
                ),
                current_runs=current,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
            )

        if cpu_percent >= self._policy.max_cpu_percent:
            return ThrottleDecision(
                allowed=False,
                reason=(
                    f"CPU usage ({cpu_percent:.1f}%) "
                    f">= threshold ({self._policy.max_cpu_percent:.1f}%)"
                ),
                current_runs=current,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
            )

        if memory_percent >= self._policy.max_memory_percent:
            return ThrottleDecision(
                allowed=False,
                reason=(
                    f"Memory usage ({memory_percent:.1f}%) "
                    f">= threshold ({self._policy.max_memory_percent:.1f}%)"
                ),
                current_runs=current,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
            )

        return ThrottleDecision(
            allowed=True,
            reason="",
            current_runs=current,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
        )


# ---------------------------------------------------------------------------
# RunQueue
# ---------------------------------------------------------------------------


class RunQueue:
    """FIFO queue for conversation runs waiting on capacity."""

    def __init__(self, throttle: CapacityThrottle) -> None:
        self._throttle = throttle
        self._queue: list[str] = []

    def enqueue(self, conversation_id: str) -> int:
        """Add *conversation_id* to the queue and return its 0-indexed position.

        Idempotent: if already queued, returns existing position.
        """
        try:
            return self._queue.index(conversation_id)
        except ValueError:
            pass
        self._queue.append(conversation_id)
        return len(self._queue) - 1

    def dequeue(self) -> str | None:
        """Pop the next conversation from the front of the queue, or ``None``."""
        if not self._queue:
            return None
        return self._queue.pop(0)

    def position(self, conversation_id: str) -> int | None:
        """Return the 0-indexed queue position, or ``None`` if not queued."""
        try:
            return self._queue.index(conversation_id)
        except ValueError:
            return None

    def pending(self) -> list[str]:
        """Return queued conversation IDs in order."""
        return list(self._queue)

    def remove(self, conversation_id: str) -> bool:
        """Remove *conversation_id* from the queue. Return ``True`` if found."""
        try:
            self._queue.remove(conversation_id)
            return True
        except ValueError:
            return False

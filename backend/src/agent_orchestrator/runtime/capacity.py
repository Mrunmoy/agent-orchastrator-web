"""Capacity telemetry snapshot (OPS-003).

Reads CPU load and RAM usage via ``psutil``, packages results into a
``CapacitySnapshot`` dataclass, and evaluates capacity gates to decide
whether a new agent run may be launched.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import psutil

# ---------------------------------------------------------------------------
# Default thresholds (from spec 06)
# ---------------------------------------------------------------------------

CPU_MAX_PERCENT: float = 85.0
"""Deny new runs when 1-min CPU load percent >= this value."""

RAM_MIN_FREE_MB: int = 2048
"""Deny new runs when free RAM (total - used) <= this value in MB."""

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapacitySnapshot:
    """Point-in-time machine resource reading.

    Field names mirror the ``resource_snapshot`` table from the domain model.
    """

    cpu_load_1m: float
    ram_used_mb: int
    ram_total_mb: int
    gpu_json: str
    agent_capacity_available: int
    captured_at: str


@dataclass(frozen=True)
class CapacityVerdict:
    """Result of evaluating capacity gates against a snapshot."""

    allowed: bool
    reason: str | None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def capture_snapshot(agent_capacity_available: int = 0) -> CapacitySnapshot:
    """Read current CPU and RAM metrics and return a ``CapacitySnapshot``.

    Parameters
    ----------
    agent_capacity_available:
        Number of agent slots still available (caller-supplied; this module
        does not track running agents).
    """
    load_1m, _load_5m, _load_15m = psutil.getloadavg()
    cpu_count = psutil.cpu_count() or 1
    cpu_percent = (load_1m / cpu_count) * 100.0

    vmem = psutil.virtual_memory()
    ram_total_mb = int(vmem.total / (1024 * 1024))
    ram_used_mb = int(vmem.used / (1024 * 1024))

    return CapacitySnapshot(
        cpu_load_1m=round(cpu_percent, 2),
        ram_used_mb=ram_used_mb,
        ram_total_mb=ram_total_mb,
        gpu_json="[]",
        agent_capacity_available=agent_capacity_available,
        captured_at=datetime.now(UTC).isoformat(),
    )


def check_capacity(
    snapshot: CapacitySnapshot,
    *,
    active_runs: int,
    max_active_runs: int,
    cpu_max_percent: float = CPU_MAX_PERCENT,
    ram_min_free_mb: int = RAM_MIN_FREE_MB,
) -> CapacityVerdict:
    """Evaluate capacity gates and return a verdict.

    Gates are checked in order: CPU, RAM, active runs.  The first failing
    gate produces a denial with a descriptive reason string.

    Parameters
    ----------
    snapshot:
        A ``CapacitySnapshot`` (typically from ``capture_snapshot``).
    active_runs:
        Number of agent runs currently in progress.
    max_active_runs:
        Maximum concurrent agent runs allowed.
    cpu_max_percent:
        CPU load percent threshold (deny if ``>=``).
    ram_min_free_mb:
        Minimum free RAM in MB (deny if ``<=``).
    """
    # Gate 1: CPU
    if snapshot.cpu_load_1m >= cpu_max_percent:
        return CapacityVerdict(
            allowed=False,
            reason=(
                f"CPU load {snapshot.cpu_load_1m:.1f}% >= " f"threshold {cpu_max_percent:.1f}%"
            ),
        )

    # Gate 2: RAM
    free_mb = snapshot.ram_total_mb - snapshot.ram_used_mb
    if free_mb <= ram_min_free_mb:
        return CapacityVerdict(
            allowed=False,
            reason=(f"RAM free {free_mb} MB <= " f"threshold {ram_min_free_mb} MB"),
        )

    # Gate 3: active runs
    if active_runs >= max_active_runs:
        return CapacityVerdict(
            allowed=False,
            reason=(f"Active runs {active_runs} >= " f"max {max_active_runs}"),
        )

    return CapacityVerdict(allowed=True, reason=None)

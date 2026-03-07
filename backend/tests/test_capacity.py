"""Tests for OPS-003: Capacity telemetry snapshot.

All psutil calls are mocked so tests do not depend on actual system state.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from agent_orchestrator.runtime.capacity import (
    CPU_MAX_PERCENT,
    RAM_MIN_FREE_MB,
    CapacitySnapshot,
    CapacityVerdict,
    capture_snapshot,
    check_capacity,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_snapshot(
    cpu_load_1m: float = 0.5,
    ram_used_mb: int = 4096,
    ram_total_mb: int = 16384,
    gpu_json: str = "[]",
    agent_capacity_available: int = 4,
    captured_at: str = "2026-03-07T00:00:00+00:00",
) -> CapacitySnapshot:
    return CapacitySnapshot(
        cpu_load_1m=cpu_load_1m,
        ram_used_mb=ram_used_mb,
        ram_total_mb=ram_total_mb,
        gpu_json=gpu_json,
        agent_capacity_available=agent_capacity_available,
        captured_at=captured_at,
    )


class _FakeVMem:
    """Mimics psutil's svmem named tuple."""

    def __init__(self, total: int, used: int):
        self.total = total
        self.used = used


# ---------------------------------------------------------------------------
# CapacitySnapshot dataclass
# ---------------------------------------------------------------------------


class TestCapacitySnapshotDataclass:
    def test_fields_present(self):
        snap = _make_snapshot()
        assert snap.cpu_load_1m == 0.5
        assert snap.ram_used_mb == 4096
        assert snap.ram_total_mb == 16384
        assert snap.gpu_json == "[]"
        assert snap.agent_capacity_available == 4
        assert snap.captured_at == "2026-03-07T00:00:00+00:00"

    def test_frozen(self):
        snap = _make_snapshot()
        with pytest.raises(AttributeError):
            snap.cpu_load_1m = 99.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CapacityVerdict dataclass
# ---------------------------------------------------------------------------


class TestCapacityVerdictDataclass:
    def test_allowed_verdict(self):
        v = CapacityVerdict(allowed=True, reason=None)
        assert v.allowed is True
        assert v.reason is None

    def test_denied_verdict(self):
        v = CapacityVerdict(allowed=False, reason="CPU overloaded")
        assert v.allowed is False
        assert v.reason == "CPU overloaded"

    def test_frozen(self):
        v = CapacityVerdict(allowed=True, reason=None)
        with pytest.raises(AttributeError):
            v.allowed = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Default constants
# ---------------------------------------------------------------------------


class TestDefaultConstants:
    def test_cpu_max_percent(self):
        assert CPU_MAX_PERCENT == 85.0

    def test_ram_min_free_mb(self):
        assert RAM_MIN_FREE_MB == 2048


# ---------------------------------------------------------------------------
# capture_snapshot()
# ---------------------------------------------------------------------------


class TestCaptureSnapshot:
    @patch("agent_orchestrator.runtime.capacity.psutil")
    def test_returns_snapshot_with_correct_values(self, mock_psutil):
        # 1-min load average = 2.5 on a 4-core machine -> 62.5%
        mock_psutil.getloadavg.return_value = (2.5, 3.0, 3.5)
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.virtual_memory.return_value = _FakeVMem(
            total=16 * 1024**3,  # 16 GiB in bytes
            used=8 * 1024**3,  # 8 GiB in bytes
        )

        snap = capture_snapshot(agent_capacity_available=3)

        assert snap.cpu_load_1m == pytest.approx(62.5)
        assert snap.ram_used_mb == 8192
        assert snap.ram_total_mb == 16384
        assert snap.gpu_json == "[]"
        assert snap.agent_capacity_available == 3
        # captured_at should be a valid ISO timestamp
        dt = datetime.fromisoformat(snap.captured_at)
        assert dt.tzinfo is not None  # timezone-aware

    @patch("agent_orchestrator.runtime.capacity.psutil")
    def test_default_agent_capacity_zero(self, mock_psutil):
        mock_psutil.getloadavg.return_value = (1.0, 1.0, 1.0)
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.virtual_memory.return_value = _FakeVMem(
            total=8 * 1024**3,
            used=4 * 1024**3,
        )

        snap = capture_snapshot()
        assert snap.agent_capacity_available == 0


# ---------------------------------------------------------------------------
# check_capacity() — CPU gate
# ---------------------------------------------------------------------------


class TestCheckCapacityCPU:
    def test_denied_when_cpu_exceeds_threshold(self):
        snap = _make_snapshot(cpu_load_1m=90.0, ram_used_mb=4096, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5)
        assert verdict.allowed is False
        assert "cpu" in verdict.reason.lower()

    def test_denied_at_exact_cpu_threshold(self):
        snap = _make_snapshot(cpu_load_1m=85.0)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5)
        assert verdict.allowed is False
        assert "cpu" in verdict.reason.lower()

    def test_allowed_just_below_cpu_threshold(self):
        snap = _make_snapshot(cpu_load_1m=84.9)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5)
        assert verdict.allowed is True


# ---------------------------------------------------------------------------
# check_capacity() — RAM gate
# ---------------------------------------------------------------------------


class TestCheckCapacityRAM:
    def test_denied_when_ram_free_below_threshold(self):
        # total=16384, used=15000 -> free=1384 < 2048
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=15000, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5)
        assert verdict.allowed is False
        assert "ram" in verdict.reason.lower()

    def test_denied_at_exact_ram_threshold(self):
        # total=16384, used=14336 -> free=2048 exactly -> denied (need > 2048)
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=14336, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5)
        assert verdict.allowed is False
        assert "ram" in verdict.reason.lower()

    def test_allowed_just_above_ram_threshold(self):
        # total=16384, used=14335 -> free=2049 > 2048
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=14335, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5)
        assert verdict.allowed is True


# ---------------------------------------------------------------------------
# check_capacity() — active runs gate
# ---------------------------------------------------------------------------


class TestCheckCapacityActiveRuns:
    def test_denied_when_active_runs_at_max(self):
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=4096, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=5, max_active_runs=5)
        assert verdict.allowed is False
        assert "active" in verdict.reason.lower() or "run" in verdict.reason.lower()

    def test_denied_when_active_runs_exceed_max(self):
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=4096, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=6, max_active_runs=5)
        assert verdict.allowed is False

    def test_allowed_when_active_runs_below_max(self):
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=4096, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=4, max_active_runs=5)
        assert verdict.allowed is True


# ---------------------------------------------------------------------------
# check_capacity() — all gates pass
# ---------------------------------------------------------------------------


class TestCheckCapacityAllPass:
    def test_allowed_when_all_gates_pass(self):
        snap = _make_snapshot(cpu_load_1m=50.0, ram_used_mb=4096, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=2, max_active_runs=5)
        assert verdict.allowed is True
        assert verdict.reason is None


# ---------------------------------------------------------------------------
# check_capacity() — custom thresholds
# ---------------------------------------------------------------------------


class TestCheckCapacityCustomThresholds:
    def test_custom_cpu_threshold(self):
        snap = _make_snapshot(cpu_load_1m=70.0)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5, cpu_max_percent=60.0)
        assert verdict.allowed is False

    def test_custom_ram_threshold(self):
        # free = 16384 - 14000 = 2384; custom threshold = 3000
        snap = _make_snapshot(cpu_load_1m=10.0, ram_used_mb=14000, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=0, max_active_runs=5, ram_min_free_mb=3000)
        assert verdict.allowed is False


# ---------------------------------------------------------------------------
# check_capacity() — first failing gate wins
# ---------------------------------------------------------------------------


class TestCheckCapacityFirstFailure:
    def test_cpu_checked_first(self):
        """When multiple gates fail, CPU is reported first."""
        snap = _make_snapshot(cpu_load_1m=90.0, ram_used_mb=15000, ram_total_mb=16384)
        verdict = check_capacity(snap, active_runs=10, max_active_runs=5)
        assert verdict.allowed is False
        assert "cpu" in verdict.reason.lower()

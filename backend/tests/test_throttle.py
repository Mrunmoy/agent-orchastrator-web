"""Tests for capacity-aware throttle and run queue (ORCH-006)."""

from __future__ import annotations

import pytest

from agent_orchestrator.orchestrator.throttle import (
    CapacityThrottle,
    RunQueue,
    ThrottleDecision,
    ThrottlePolicy,
)


# ---------------------------------------------------------------------------
# ThrottlePolicy defaults
# ---------------------------------------------------------------------------


class TestThrottlePolicyDefaults:
    def test_default_max_concurrent_runs(self) -> None:
        policy = ThrottlePolicy()
        assert policy.max_concurrent_runs == 3

    def test_default_max_cpu_percent(self) -> None:
        policy = ThrottlePolicy()
        assert policy.max_cpu_percent == 85.0

    def test_default_max_memory_percent(self) -> None:
        policy = ThrottlePolicy()
        assert policy.max_memory_percent == 90.0

    def test_custom_values(self) -> None:
        policy = ThrottlePolicy(
            max_concurrent_runs=5,
            max_cpu_percent=70.0,
            max_memory_percent=80.0,
        )
        assert policy.max_concurrent_runs == 5
        assert policy.max_cpu_percent == 70.0
        assert policy.max_memory_percent == 80.0


# ---------------------------------------------------------------------------
# CapacityThrottle.check – allow / deny scenarios
# ---------------------------------------------------------------------------


class TestThrottleCheck:
    def test_allows_when_under_all_limits(self) -> None:
        throttle = CapacityThrottle()
        decision = throttle.check(cpu_percent=50.0, memory_percent=60.0)
        assert decision.allowed is True
        assert decision.reason == ""
        assert decision.current_runs == 0
        assert decision.cpu_percent == 50.0
        assert decision.memory_percent == 60.0

    def test_denies_when_runs_at_max(self) -> None:
        throttle = CapacityThrottle(ThrottlePolicy(max_concurrent_runs=2))
        throttle.register_run("conv-1")
        throttle.register_run("conv-2")
        decision = throttle.check(cpu_percent=10.0, memory_percent=20.0)
        assert decision.allowed is False
        assert "concurrent" in decision.reason.lower() or "run" in decision.reason.lower()
        assert decision.current_runs == 2

    def test_denies_when_cpu_too_high(self) -> None:
        throttle = CapacityThrottle(ThrottlePolicy(max_cpu_percent=80.0))
        decision = throttle.check(cpu_percent=85.0, memory_percent=50.0)
        assert decision.allowed is False
        assert "cpu" in decision.reason.lower()
        assert decision.cpu_percent == 85.0

    def test_denies_when_cpu_exactly_at_threshold(self) -> None:
        throttle = CapacityThrottle(ThrottlePolicy(max_cpu_percent=80.0))
        decision = throttle.check(cpu_percent=80.0, memory_percent=50.0)
        assert decision.allowed is False

    def test_denies_when_memory_too_high(self) -> None:
        throttle = CapacityThrottle(ThrottlePolicy(max_memory_percent=90.0))
        decision = throttle.check(cpu_percent=50.0, memory_percent=95.0)
        assert decision.allowed is False
        assert "memory" in decision.reason.lower()
        assert decision.memory_percent == 95.0

    def test_denies_when_memory_exactly_at_threshold(self) -> None:
        throttle = CapacityThrottle(ThrottlePolicy(max_memory_percent=90.0))
        decision = throttle.check(cpu_percent=50.0, memory_percent=90.0)
        assert decision.allowed is False


# ---------------------------------------------------------------------------
# CapacityThrottle – run tracking
# ---------------------------------------------------------------------------


class TestRunTracking:
    def test_register_and_active_runs(self) -> None:
        throttle = CapacityThrottle()
        throttle.register_run("conv-a")
        throttle.register_run("conv-b")
        assert sorted(throttle.active_runs()) == ["conv-a", "conv-b"]

    def test_release_run(self) -> None:
        throttle = CapacityThrottle()
        throttle.register_run("conv-a")
        throttle.register_run("conv-b")
        throttle.release_run("conv-a")
        assert throttle.active_runs() == ["conv-b"]

    def test_release_unknown_run_is_noop(self) -> None:
        throttle = CapacityThrottle()
        throttle.release_run("nonexistent")  # should not raise
        assert throttle.active_runs() == []

    def test_register_duplicate_run_is_idempotent(self) -> None:
        throttle = CapacityThrottle()
        throttle.register_run("conv-a")
        throttle.register_run("conv-a")
        assert throttle.active_runs() == ["conv-a"]

    def test_active_runs_empty_initially(self) -> None:
        throttle = CapacityThrottle()
        assert throttle.active_runs() == []


# ---------------------------------------------------------------------------
# RunQueue – FIFO ordering
# ---------------------------------------------------------------------------


class TestRunQueue:
    def test_enqueue_returns_position(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        pos0 = queue.enqueue("conv-1")
        pos1 = queue.enqueue("conv-2")
        assert pos0 == 0
        assert pos1 == 1

    def test_dequeue_fifo_order(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        queue.enqueue("conv-1")
        queue.enqueue("conv-2")
        queue.enqueue("conv-3")
        assert queue.dequeue() == "conv-1"
        assert queue.dequeue() == "conv-2"
        assert queue.dequeue() == "conv-3"
        assert queue.dequeue() is None

    def test_position_tracking(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        queue.enqueue("conv-a")
        queue.enqueue("conv-b")
        queue.enqueue("conv-c")
        assert queue.position("conv-a") == 0
        assert queue.position("conv-b") == 1
        assert queue.position("conv-c") == 2
        assert queue.position("conv-unknown") is None

    def test_pending_returns_ordered_list(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        queue.enqueue("conv-x")
        queue.enqueue("conv-y")
        assert queue.pending() == ["conv-x", "conv-y"]

    def test_remove_existing(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        queue.enqueue("conv-1")
        queue.enqueue("conv-2")
        queue.enqueue("conv-3")
        assert queue.remove("conv-2") is True
        assert queue.pending() == ["conv-1", "conv-3"]

    def test_remove_nonexistent(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        assert queue.remove("nope") is False

    def test_enqueue_duplicate_is_idempotent(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        pos0 = queue.enqueue("conv-1")
        queue.enqueue("conv-2")
        pos_dup = queue.enqueue("conv-1")
        assert pos_dup == pos0
        assert queue.pending() == ["conv-1", "conv-2"]

    def test_position_updates_after_dequeue(self) -> None:
        throttle = CapacityThrottle()
        queue = RunQueue(throttle)
        queue.enqueue("conv-1")
        queue.enqueue("conv-2")
        queue.dequeue()  # removes conv-1
        assert queue.position("conv-2") == 0

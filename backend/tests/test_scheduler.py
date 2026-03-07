"""Tests for the round-robin scheduler (ORCH-003)."""

from __future__ import annotations

from agent_orchestrator.orchestrator.models import (
    Agent,
    AgentRole,
    AgentStatus,
    Provider,
)
from agent_orchestrator.orchestrator.scheduler import RoundRobinScheduler


def _make_agent(
    id: str,
    status: AgentStatus = AgentStatus.IDLE,
    name: str | None = None,
) -> Agent:
    """Helper to build a minimal Agent fixture."""
    return Agent(
        id=id,
        display_name=name or f"agent-{id}",
        provider=Provider.CLAUDE,
        model="claude-sonnet",
        role=AgentRole.WORKER,
        status=status,
        capabilities_json="{}",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


# ── Round-robin ordering ────────────────────────────────────────────────


class TestRoundRobinOrdering:
    def test_cycles_through_agents_in_order(self) -> None:
        agents = [_make_agent("a"), _make_agent("b"), _make_agent("c")]
        sched = RoundRobinScheduler(agents)

        assert sched.next_agent().id == "a"  # type: ignore[union-attr]
        assert sched.next_agent().id == "b"  # type: ignore[union-attr]
        assert sched.next_agent().id == "c"  # type: ignore[union-attr]

    def test_wrap_around_cycles_back_to_beginning(self) -> None:
        agents = [_make_agent("a"), _make_agent("b")]
        sched = RoundRobinScheduler(agents)

        assert sched.next_agent().id == "a"  # type: ignore[union-attr]
        assert sched.next_agent().id == "b"  # type: ignore[union-attr]
        # Should wrap around
        assert sched.next_agent().id == "a"  # type: ignore[union-attr]

    def test_single_agent_roster(self) -> None:
        agents = [_make_agent("only")]
        sched = RoundRobinScheduler(agents)

        assert sched.next_agent().id == "only"  # type: ignore[union-attr]
        assert sched.next_agent().id == "only"  # type: ignore[union-attr]


# ── Skipping unavailable agents ─────────────────────────────────────────


class TestSkipUnavailable:
    def test_skips_blocked_agents(self) -> None:
        agents = [
            _make_agent("a", AgentStatus.BLOCKED),
            _make_agent("b", AgentStatus.IDLE),
        ]
        sched = RoundRobinScheduler(agents)

        assert sched.next_agent().id == "b"  # type: ignore[union-attr]

    def test_skips_offline_agents(self) -> None:
        agents = [
            _make_agent("a", AgentStatus.OFFLINE),
            _make_agent("b", AgentStatus.IDLE),
        ]
        sched = RoundRobinScheduler(agents)

        assert sched.next_agent().id == "b"  # type: ignore[union-attr]

    def test_returns_none_when_all_agents_unavailable(self) -> None:
        agents = [
            _make_agent("a", AgentStatus.BLOCKED),
            _make_agent("b", AgentStatus.OFFLINE),
        ]
        sched = RoundRobinScheduler(agents)

        assert sched.next_agent() is None

    def test_empty_roster_returns_none(self) -> None:
        sched = RoundRobinScheduler([])
        assert sched.next_agent() is None


# ── Reset ───────────────────────────────────────────────────────────────


class TestReset:
    def test_reset_returns_to_first_agent(self) -> None:
        agents = [_make_agent("a"), _make_agent("b"), _make_agent("c")]
        sched = RoundRobinScheduler(agents)

        sched.next_agent()  # a
        sched.next_agent()  # b
        assert sched.current_index == 2

        sched.reset()
        assert sched.current_index == 0
        assert sched.next_agent().id == "a"  # type: ignore[union-attr]


# ── available_agents property ───────────────────────────────────────────


class TestAvailableAgents:
    def test_filters_correctly(self) -> None:
        agents = [
            _make_agent("a", AgentStatus.IDLE),
            _make_agent("b", AgentStatus.RUNNING),
            _make_agent("c", AgentStatus.BLOCKED),
            _make_agent("d", AgentStatus.OFFLINE),
        ]
        sched = RoundRobinScheduler(agents)

        available = sched.available_agents
        available_ids = [a.id for a in available]
        assert available_ids == ["a", "b"]


# ── mark_agent_status ──────────────────────────────────────────────────


class TestMarkAgentStatus:
    def test_updates_roster(self) -> None:
        agents = [_make_agent("a", AgentStatus.IDLE)]
        sched = RoundRobinScheduler(agents)

        sched.mark_agent_status("a", AgentStatus.BLOCKED)

        assert sched.next_agent() is None

    def test_mark_status_unknown_agent_is_noop(self) -> None:
        agents = [_make_agent("a")]
        sched = RoundRobinScheduler(agents)

        # Should not raise
        sched.mark_agent_status("nonexistent", AgentStatus.BLOCKED)
        assert sched.next_agent().id == "a"  # type: ignore[union-attr]

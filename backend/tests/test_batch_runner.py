"""Tests for the BatchRunner (ORCH-004)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus
from agent_orchestrator.orchestrator.batch_runner import (
    BatchRunner,
)
from agent_orchestrator.orchestrator.models import (
    Agent,
    AgentRole,
    AgentStatus,
    ConversationState,
    Provider,
    RunStatus,
)
from agent_orchestrator.orchestrator.scheduler import RoundRobinScheduler
from agent_orchestrator.orchestrator.state_machine import StateMachine

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent(agent_id: str, status: AgentStatus = AgentStatus.IDLE) -> Agent:
    return Agent(
        id=agent_id,
        display_name=agent_id,
        provider=Provider.CLAUDE,
        model="sonnet",
        role=AgentRole.WORKER,
        status=status,
        capabilities_json="{}",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


def _make_adapter(text: str = "ok", status: AdapterStatus = AdapterStatus.IDLE) -> AsyncMock:
    adapter = AsyncMock()
    adapter.send_prompt.return_value = AdapterResult(text=text, status=status)
    return adapter


def _build_runner(
    agents: list[Agent] | None = None,
    adapter_map: dict[str, AsyncMock] | None = None,
    batch_size: int = 20,
) -> BatchRunner:
    if agents is None:
        agents = [_make_agent("a1"), _make_agent("a2")]
    if adapter_map is None:
        adapter_map = {a.id: _make_adapter() for a in agents}
    scheduler = RoundRobinScheduler(agents)
    sm = StateMachine("conv-1", ConversationState.AUTONOMOUS_WORK)
    return BatchRunner(
        conversation_id="conv-1",
        scheduler=scheduler,
        state_machine=sm,
        adapter_map=adapter_map,
        batch_size=batch_size,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_runs_n_turns() -> None:
    """Runner completes batch_size turns with round-robin agents."""
    runner = _build_runner(batch_size=6)
    result = await runner.run()

    assert result.turns_completed == 6
    assert result.status == RunStatus.DONE
    assert len(result.turn_log) == 6
    assert result.conversation_id == "conv-1"


@pytest.mark.asyncio
async def test_turns_completed_property() -> None:
    """turns_completed property tracks correctly during and after run."""
    runner = _build_runner(batch_size=4)
    assert runner.turns_completed == 0
    await runner.run()
    assert runner.turns_completed == 4


@pytest.mark.asyncio
async def test_turn_log_contains_correct_records() -> None:
    """Each TurnRecord has correct fields."""
    agents = [_make_agent("a1"), _make_agent("a2")]
    adapters = {
        "a1": _make_adapter(text="reply-a1"),
        "a2": _make_adapter(text="reply-a2"),
    }
    runner = _build_runner(agents=agents, adapter_map=adapters, batch_size=4)
    result = await runner.run()

    # Round-robin: a1, a2, a1, a2
    assert result.turn_log[0].agent_id == "a1"
    assert result.turn_log[0].response_text == "reply-a1"
    assert result.turn_log[0].turn_number == 1
    assert result.turn_log[0].status == AdapterStatus.IDLE

    assert result.turn_log[1].agent_id == "a2"
    assert result.turn_log[1].response_text == "reply-a2"
    assert result.turn_log[1].turn_number == 2

    assert result.turn_log[2].agent_id == "a1"
    assert result.turn_log[3].agent_id == "a2"

    # All records have timestamps
    for rec in result.turn_log:
        assert rec.timestamp != ""


@pytest.mark.asyncio
async def test_pause_stops_mid_batch() -> None:
    """pause() causes run() to return PAUSED status."""
    agents = [_make_agent("a1")]
    call_count = 0

    async def _slow_send(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 3:
            runner.pause()
        return AdapterResult(text="ok", status=AdapterStatus.IDLE)

    adapter = AsyncMock()
    adapter.send_prompt.side_effect = _slow_send

    runner = _build_runner(agents=agents, adapter_map={"a1": adapter}, batch_size=20)
    result = await runner.run()

    assert result.status == RunStatus.PAUSED
    assert result.turns_completed == 3
    assert runner.status == RunStatus.PAUSED


@pytest.mark.asyncio
async def test_stop_stops_mid_batch() -> None:
    """stop() causes run() to return DONE status."""
    agents = [_make_agent("a1")]
    call_count = 0

    async def _slow_send(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            runner.stop()
        return AdapterResult(text="ok", status=AdapterStatus.IDLE)

    adapter = AsyncMock()
    adapter.send_prompt.side_effect = _slow_send

    runner = _build_runner(agents=agents, adapter_map={"a1": adapter}, batch_size=20)
    result = await runner.run()

    assert result.status == RunStatus.DONE
    assert result.turns_completed == 2


@pytest.mark.asyncio
async def test_no_agents_available_returns_early() -> None:
    """When scheduler returns None, runner returns WAITING_RESOURCES."""
    agents = [_make_agent("a1", status=AgentStatus.OFFLINE)]
    adapter = _make_adapter()
    runner = _build_runner(agents=agents, adapter_map={"a1": adapter}, batch_size=10)
    result = await runner.run()

    assert result.status == RunStatus.WAITING_RESOURCES
    assert result.turns_completed == 0
    adapter.send_prompt.assert_not_called()


@pytest.mark.asyncio
async def test_adapter_timeout_recorded_but_continues() -> None:
    """TIMED_OUT adapter result is recorded; batch continues."""
    agents = [_make_agent("a1"), _make_agent("a2")]
    adapters = {
        "a1": _make_adapter(text="timeout!", status=AdapterStatus.TIMED_OUT),
        "a2": _make_adapter(text="ok"),
    }
    runner = _build_runner(agents=agents, adapter_map=adapters, batch_size=4)
    result = await runner.run()

    assert result.turns_completed == 4
    assert result.status == RunStatus.DONE
    # a1 turns should have TIMED_OUT status
    a1_turns = [r for r in result.turn_log if r.agent_id == "a1"]
    assert all(r.status == AdapterStatus.TIMED_OUT for r in a1_turns)
    # a2 turns should be fine
    a2_turns = [r for r in result.turn_log if r.agent_id == "a2"]
    assert all(r.status == AdapterStatus.IDLE for r in a2_turns)


@pytest.mark.asyncio
async def test_adapter_error_recorded_but_continues() -> None:
    """ERROR adapter result is recorded; batch continues."""
    agents = [_make_agent("a1"), _make_agent("a2")]
    adapters = {
        "a1": _make_adapter(text="err!", status=AdapterStatus.ERROR),
        "a2": _make_adapter(text="ok"),
    }
    runner = _build_runner(agents=agents, adapter_map=adapters, batch_size=4)
    result = await runner.run()

    assert result.turns_completed == 4
    assert result.status == RunStatus.DONE
    a1_turns = [r for r in result.turn_log if r.agent_id == "a1"]
    assert all(r.status == AdapterStatus.ERROR for r in a1_turns)


@pytest.mark.asyncio
async def test_status_property_reflects_run_state() -> None:
    """status property is QUEUED before run, RUNNING during, DONE after."""
    runner = _build_runner(batch_size=2)
    assert runner.status == RunStatus.QUEUED

    observed_status: list[RunStatus] = []

    async def _observe(*args, **kwargs):
        observed_status.append(runner.status)
        return AdapterResult(text="ok", status=AdapterStatus.IDLE)

    # Replace both adapters
    for aid in runner._adapter_map:
        adapter = AsyncMock()
        adapter.send_prompt.side_effect = _observe
        runner._adapter_map[aid] = adapter

    await runner.run()
    assert runner.status == RunStatus.DONE
    assert all(s == RunStatus.RUNNING for s in observed_status)


@pytest.mark.asyncio
async def test_adapter_exception_recorded_as_error() -> None:
    """If adapter.send_prompt raises, record ERROR and continue."""
    agents = [_make_agent("a1"), _make_agent("a2")]
    bad_adapter = AsyncMock()
    bad_adapter.send_prompt.side_effect = RuntimeError("boom")
    adapters = {
        "a1": bad_adapter,
        "a2": _make_adapter(text="ok"),
    }
    runner = _build_runner(agents=agents, adapter_map=adapters, batch_size=4)
    result = await runner.run()

    assert result.turns_completed == 4
    assert result.status == RunStatus.DONE
    a1_turns = [r for r in result.turn_log if r.agent_id == "a1"]
    assert all(r.status == AdapterStatus.ERROR for r in a1_turns)

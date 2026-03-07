"""20-turn batch runner for agent orchestration (ORCH-004).

Coordinates a conversation run: takes a roster of agents and runs them
in round-robin order for up to N turns (default 20), with pause/continue/stop
controls.  Pure logic + async — no DB writes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from agent_orchestrator.adapters.base import AdapterStatus, BaseAdapter
from agent_orchestrator.orchestrator.models import AgentStatus, RunStatus
from agent_orchestrator.orchestrator.scheduler import RoundRobinScheduler
from agent_orchestrator.orchestrator.state_machine import StateMachine

# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------


@dataclass
class TurnRecord:
    """Record of a single agent turn within a batch."""

    turn_number: int
    agent_id: str
    prompt: str
    response_text: str
    status: AdapterStatus
    timestamp: str


@dataclass
class BatchResult:
    """Outcome of a batch run."""

    conversation_id: str
    turns_completed: int
    status: RunStatus
    turn_log: list[TurnRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# BatchRunner
# ---------------------------------------------------------------------------


class BatchRunner:
    """Run agents in round-robin order for up to *batch_size* turns."""

    def __init__(
        self,
        conversation_id: str,
        scheduler: RoundRobinScheduler,
        state_machine: StateMachine,
        adapter_map: dict[str, BaseAdapter],
        batch_size: int = 20,
    ) -> None:
        self._conversation_id = conversation_id
        self._scheduler = scheduler
        self._state_machine = state_machine
        self._adapter_map = adapter_map
        self._batch_size = batch_size

        self._status = RunStatus.QUEUED
        self._turns_completed = 0
        self._turn_log: list[TurnRecord] = []
        self._pause_requested = False
        self._stop_requested = False

    # -- Properties ----------------------------------------------------------

    @property
    def status(self) -> RunStatus:
        return self._status

    @property
    def turns_completed(self) -> int:
        return self._turns_completed

    # -- Controls ------------------------------------------------------------

    def pause(self) -> None:
        """Request the batch to pause after the current turn."""
        self._pause_requested = True

    def stop(self) -> None:
        """Request the batch to stop after the current turn."""
        self._stop_requested = True

    # -- Main loop -----------------------------------------------------------

    async def run(self) -> BatchResult:
        """Execute the batch run, returning a :class:`BatchResult`."""
        self._status = RunStatus.RUNNING

        for turn_num in range(1, self._batch_size + 1):
            # Get next agent from scheduler
            agent = self._scheduler.next_agent()
            if agent is None:
                self._status = RunStatus.WAITING_RESOURCES
                break

            # Build prompt
            prompt = (
                f"Continue the conversation. "
                f"Turn {turn_num}/{self._batch_size}"
            )

            # Mark agent as running
            self._scheduler.mark_agent_status(agent.id, AgentStatus.RUNNING)

            # Call adapter (lookup + invocation guarded together)
            try:
                adapter = self._adapter_map[agent.id]
                result = await adapter.send_prompt(
                    prompt,
                    working_dir=".",
                )
                record = TurnRecord(
                    turn_number=turn_num,
                    agent_id=agent.id,
                    prompt=prompt,
                    response_text=result.text,
                    status=result.status,
                    timestamp=datetime.now(UTC).isoformat(),
                )
            except Exception:
                record = TurnRecord(
                    turn_number=turn_num,
                    agent_id=agent.id,
                    prompt=prompt,
                    response_text="",
                    status=AdapterStatus.ERROR,
                    timestamp=datetime.now(UTC).isoformat(),
                )
            finally:
                # Always reset agent to idle
                self._scheduler.mark_agent_status(agent.id, AgentStatus.IDLE)

            self._turn_log.append(record)
            self._turns_completed = turn_num

            # Check pause/stop between turns
            if self._pause_requested:
                self._status = RunStatus.PAUSED
                break
            if self._stop_requested:
                self._status = RunStatus.DONE
                break
        else:
            # Completed all turns without break
            self._status = RunStatus.DONE

        return BatchResult(
            conversation_id=self._conversation_id,
            turns_completed=self._turns_completed,
            status=self._status,
            turn_log=list(self._turn_log),
        )

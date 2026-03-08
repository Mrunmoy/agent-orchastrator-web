"""Background batch executor service (T-401).

Polls the ``scheduler_run`` table for queued runs, instantiates a
:class:`BatchRunner` with the appropriate adapters, executes turns, and
writes each turn result as a :class:`MessageEvent` to the database.
"""

from __future__ import annotations

import abc
import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime

from agent_orchestrator.adapters.base import BaseAdapter
from agent_orchestrator.adapters.claude_adapter import ClaudeAdapter
from agent_orchestrator.adapters.codex_adapter import CodexAdapter
from agent_orchestrator.orchestrator.batch_runner import BatchRunner
from agent_orchestrator.orchestrator.models import (
    Agent,
    AgentRole,
    AgentStatus,
    ConversationState,
    MessageEvent,
    Provider,
    RunStatus,
)
from agent_orchestrator.orchestrator.scheduler import RoundRobinScheduler
from agent_orchestrator.orchestrator.state_machine import StateMachine
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_message_event import (
    SQLiteMessageEventRepository,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Adapter factory (injectable for testing)
# ---------------------------------------------------------------------------

_AGENT_COLUMNS = [
    "id",
    "display_name",
    "provider",
    "model",
    "personality_key",
    "role",
    "status",
    "session_id",
    "capabilities_json",
    "sort_order",
    "created_at",
    "updated_at",
]

_CA_COLUMNS = [
    "id",
    "conversation_id",
    "agent_id",
    "turn_order",
    "enabled",
    "permission_profile",
    "is_merge_coordinator",
    "created_at",
]


class AdapterFactory(abc.ABC):
    """Abstract factory for creating adapters from provider/model info."""

    @abc.abstractmethod
    def create(self, provider: str, model: str) -> BaseAdapter:
        """Return a BaseAdapter instance for the given provider."""


class DefaultAdapterFactory(AdapterFactory):
    """Creates real CLI adapters based on provider string."""

    def create(self, provider: str, model: str) -> BaseAdapter:
        if provider == "claude":
            return ClaudeAdapter()
        if provider == "codex":
            return CodexAdapter()
        raise ValueError(f"No adapter available for provider '{provider}'")


# ---------------------------------------------------------------------------
# BatchExecutor
# ---------------------------------------------------------------------------


class BatchExecutor:
    """Background service that polls for queued runs and executes them.

    Parameters
    ----------
    db:
        The shared :class:`DatabaseManager`.
    adapter_factory:
        Factory for creating adapter instances.  Defaults to
        :class:`DefaultAdapterFactory` which uses real CLI adapters.
    poll_interval:
        Seconds between poll cycles.  Default 2.0.
    """

    def __init__(
        self,
        db: DatabaseManager,
        *,
        adapter_factory: AdapterFactory | None = None,
        poll_interval: float = 2.0,
    ) -> None:
        self._db = db
        self._adapter_factory = adapter_factory or DefaultAdapterFactory()
        self._poll_interval = poll_interval
        self._task: asyncio.Task | None = None
        self._running = False

    # -- Lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        """Begin the background polling loop."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("BatchExecutor started (poll every %.1fs)", self._poll_interval)

    async def stop(self) -> None:
        """Stop the polling loop and wait for it to finish."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("BatchExecutor stopped")

    # -- Internal loop -------------------------------------------------------

    async def _loop(self) -> None:
        """Poll forever until cancelled."""
        while self._running:
            try:
                await self._poll_and_run()
            except Exception:
                logger.exception("BatchExecutor poll error")
            await asyncio.sleep(self._poll_interval)

    # -- Poll & execute ------------------------------------------------------

    async def _poll_and_run(self) -> None:
        """Find one queued run and execute it."""
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT id, conversation_id, batch_size "
                "FROM scheduler_run "
                "WHERE status = 'queued' "
                "ORDER BY created_at ASC "
                "LIMIT 1",
            ).fetchone()

        if row is None:
            return

        run_id, conversation_id, batch_size = row
        await self._execute_run(run_id, conversation_id, batch_size)

    async def _execute_run(
        self,
        run_id: str,
        conversation_id: str,
        batch_size: int,
    ) -> None:
        """Execute a single batch run.

        1. Mark run as 'running'
        2. Load agents for the conversation
        3. Create adapters, scheduler, BatchRunner
        4. Run the batch
        5. Write each turn as a MessageEvent
        6. Mark run as 'done' or 'failed'
        """
        now = datetime.now(UTC).isoformat()

        # Mark running
        with self._db.connection() as conn:
            conn.execute(
                "UPDATE scheduler_run SET status = 'running', started_at = ? WHERE id = ?",
                (now, run_id),
            )
            conn.commit()

        try:
            # Load agents for conversation
            agents, adapter_map = self._load_agents_for_conversation(conversation_id)

            if not agents:
                raise ValueError(f"No agents linked to conversation '{conversation_id}'")

            # Build orchestration components
            scheduler = RoundRobinScheduler(agents)
            state_machine = StateMachine(conversation_id, ConversationState.DEBATE)
            runner = BatchRunner(
                conversation_id=conversation_id,
                scheduler=scheduler,
                state_machine=state_machine,
                adapter_map=adapter_map,
                batch_size=batch_size,
            )

            # Execute
            result = await runner.run()

            # Write each turn as a MessageEvent
            event_repo = SQLiteMessageEventRepository(self._db)
            for record in result.turn_log:
                event = MessageEvent(
                    conversation_id=conversation_id,
                    event_id=str(uuid.uuid4()),
                    source_type="agent",
                    source_id=record.agent_id,
                    text=record.response_text,
                    event_type="debate_turn",
                    metadata_json=json.dumps(
                        {
                            "turn_number": record.turn_number,
                            "run_id": run_id,
                            "adapter_status": record.status.value,
                            "prompt": record.prompt,
                        }
                    ),
                    created_at=record.timestamp,
                )
                event_repo.append(event)

            # Mark done
            ended = datetime.now(UTC).isoformat()
            final_status = "done"
            if result.status == RunStatus.FAILED:
                final_status = "failed"
            elif result.status == RunStatus.PAUSED:
                final_status = "paused"

            with self._db.connection() as conn:
                conn.execute(
                    "UPDATE scheduler_run SET status = ?, ended_at = ? WHERE id = ?",
                    (final_status, ended, run_id),
                )
                conn.commit()

            logger.info(
                "Run %s completed: %d turns, status=%s",
                run_id,
                result.turns_completed,
                final_status,
            )

        except Exception:
            logger.exception("Run %s failed", run_id)
            ended = datetime.now(UTC).isoformat()
            with self._db.connection() as conn:
                conn.execute(
                    "UPDATE scheduler_run SET status = 'failed', ended_at = ? WHERE id = ?",
                    (ended, run_id),
                )
                conn.commit()

    # -- Helpers -------------------------------------------------------------

    def _load_agents_for_conversation(
        self, conversation_id: str
    ) -> tuple[list[Agent], dict[str, BaseAdapter]]:
        """Load agents linked to a conversation and create adapters for them.

        Returns (agent_list, adapter_map) where adapter_map maps agent_id to
        a BaseAdapter instance.
        """
        with self._db.connection() as conn:
            # Get linked agent IDs in turn order
            ca_rows = conn.execute(
                "SELECT agent_id FROM conversation_agent "
                "WHERE conversation_id = ? AND enabled = 1 "
                "ORDER BY turn_order ASC",
                (conversation_id,),
            ).fetchall()

            agents: list[Agent] = []
            adapter_map: dict[str, BaseAdapter] = {}

            for (agent_id,) in ca_rows:
                row = conn.execute("SELECT * FROM agent WHERE id = ?", (agent_id,)).fetchone()
                if row is None:
                    continue

                d = dict(zip(_AGENT_COLUMNS, row))
                agent = Agent(
                    id=d["id"],
                    display_name=d["display_name"],
                    provider=Provider(d["provider"]),
                    model=d["model"],
                    role=AgentRole(d["role"]),
                    status=AgentStatus.IDLE,  # Always start idle for a new run
                    capabilities_json=d["capabilities_json"],
                    created_at=d["created_at"],
                    updated_at=d["updated_at"],
                    personality_key=d["personality_key"],
                    session_id=d["session_id"],
                    sort_order=d["sort_order"],
                )
                agents.append(agent)

                try:
                    adapter = self._adapter_factory.create(d["provider"], d["model"])
                    adapter_map[agent.id] = adapter
                except ValueError:
                    logger.warning(
                        "No adapter for agent %s (provider=%s)", agent.id, d["provider"]
                    )

        return agents, adapter_map

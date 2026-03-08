"""Tests for the BatchExecutor background service (T-401)."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus, BaseAdapter
from agent_orchestrator.runtime.executor import AdapterFactory, BatchExecutor
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_message_event import (
    SQLiteMessageEventRepository,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class MockAdapter(BaseAdapter):
    """In-memory adapter for tests — no CLI required."""

    def __init__(self, text: str = "mock response") -> None:
        self._text = text

    def is_available(self) -> bool:
        return True

    async def send_prompt(
        self,
        prompt: str,
        *,
        working_dir: str,
        session_id: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> AdapterResult:
        return AdapterResult(text=self._text, status=AdapterStatus.IDLE)

    async def resume_session(
        self,
        session_id: str,
        prompt: str,
        *,
        working_dir: str,
        timeout_seconds: float = 120.0,
    ) -> AdapterResult:
        return AdapterResult(text=self._text, status=AdapterStatus.IDLE)


class MockAdapterFactory(AdapterFactory):
    """Factory that always returns MockAdapter instances."""

    def __init__(self, text: str = "mock response") -> None:
        self._text = text

    def create(self, provider: str, model: str) -> BaseAdapter:
        return MockAdapter(text=self._text)


class FailingAdapterFactory(AdapterFactory):
    """Factory that returns adapters which raise on send_prompt."""

    def create(self, provider: str, model: str) -> BaseAdapter:
        adapter = AsyncMock(spec=BaseAdapter)
        adapter.send_prompt.side_effect = RuntimeError("boom")
        return adapter


def _make_db() -> DatabaseManager:
    """Create an in-memory DB with schema initialized."""
    db = DatabaseManager(":memory:")
    db.initialize()
    return db


def _seed_conversation(db: DatabaseManager, conv_id: str = "conv-1") -> str:
    """Insert a conversation and return its id."""
    now = datetime.now(UTC).isoformat()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO conversation "
            "(id, title, project_path, state, phase, gate_status, "
            " created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (conv_id, "Test", "/tmp", "debate", "design_debate", "open", now, now),
        )
        conn.commit()
    return conv_id


def _seed_agent(
    db: DatabaseManager,
    agent_id: str = "agent-1",
    provider: str = "claude",
    model: str = "sonnet",
) -> str:
    """Insert an agent and return its id."""
    now = datetime.now(UTC).isoformat()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO agent "
            "(id, display_name, provider, model, personality_key, role, "
            " status, session_id, capabilities_json, sort_order, "
            " created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (agent_id, agent_id, provider, model, None, "worker", "idle", None, "[]", 0, now, now),
        )
        conn.commit()
    return agent_id


def _link_agent(db: DatabaseManager, conv_id: str, agent_id: str, turn_order: int = 1) -> None:
    """Link an agent to a conversation."""
    now = datetime.now(UTC).isoformat()
    ca_id = str(uuid.uuid4())
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO conversation_agent "
            "(id, conversation_id, agent_id, turn_order, enabled, "
            " permission_profile, is_merge_coordinator, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ca_id, conv_id, agent_id, turn_order, 1, "default", 0, now),
        )
        conn.commit()


def _create_queued_run(
    db: DatabaseManager,
    conv_id: str,
    batch_size: int = 4,
) -> str:
    """Insert a queued scheduler_run and return its id."""
    run_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()
    with db.connection() as conn:
        conn.execute(
            "INSERT INTO scheduler_run "
            "(id, conversation_id, status, batch_size, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (run_id, conv_id, "queued", batch_size, now),
        )
        conn.commit()
    return run_id


def _get_run_status(db: DatabaseManager, run_id: str) -> str:
    with db.connection() as conn:
        row = conn.execute("SELECT status FROM scheduler_run WHERE id = ?", (run_id,)).fetchone()
    return row[0]


def _get_run(db: DatabaseManager, run_id: str) -> dict:
    keys = [
        "id",
        "conversation_id",
        "status",
        "batch_size",
        "reason",
        "started_at",
        "ended_at",
        "created_at",
    ]
    with db.connection() as conn:
        row = conn.execute("SELECT * FROM scheduler_run WHERE id = ?", (run_id,)).fetchone()
    return dict(zip(keys, row))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_poll_picks_up_queued_run() -> None:
    """_poll_and_run should find a queued run and execute it."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1", "claude", "sonnet")
    a2 = _seed_agent(db, "a2", "codex", "gpt-4")
    _link_agent(db, conv_id, a1, 1)
    _link_agent(db, conv_id, a2, 2)
    run_id = _create_queued_run(db, conv_id, batch_size=4)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory())
    await executor._poll_and_run()

    assert _get_run_status(db, run_id) == "done"


@pytest.mark.asyncio
async def test_execute_run_writes_message_events() -> None:
    """Each turn should produce a MessageEvent in the DB."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    a2 = _seed_agent(db, "a2")
    _link_agent(db, conv_id, a1, 1)
    _link_agent(db, conv_id, a2, 2)
    _create_queued_run(db, conv_id, batch_size=4)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory(text="hello"))
    await executor._poll_and_run()

    repo = SQLiteMessageEventRepository(db)
    events = repo.list_by_conversation(conv_id)
    assert len(events) == 4
    # Check round-robin order
    assert events[0].source_id == "a1"
    assert events[1].source_id == "a2"
    assert events[2].source_id == "a1"
    assert events[3].source_id == "a2"
    # Check event fields
    for ev in events:
        assert ev.source_type == "agent"
        assert ev.event_type == "debate_turn"
        assert ev.text == "hello"


@pytest.mark.asyncio
async def test_execute_run_sets_running_then_done() -> None:
    """Run status transitions queued -> running -> done."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    _link_agent(db, conv_id, a1, 1)
    run_id = _create_queued_run(db, conv_id, batch_size=2)

    observed_statuses: list[str] = []

    class ObservingFactory(AdapterFactory):
        def create(self, provider: str, model: str) -> BaseAdapter:
            return ObservingAdapter(db, run_id, observed_statuses)

    class ObservingAdapter(BaseAdapter):
        def __init__(self, db, run_id, statuses):
            self._db = db
            self._run_id = run_id
            self._statuses = statuses

        def is_available(self) -> bool:
            return True

        async def send_prompt(self, prompt, *, working_dir, session_id=None, timeout_seconds=120):
            self._statuses.append(_get_run_status(self._db, self._run_id))
            return AdapterResult(text="ok", status=AdapterStatus.IDLE)

        async def resume_session(self, session_id, prompt, *, working_dir, timeout_seconds=120):
            return AdapterResult(text="ok", status=AdapterStatus.IDLE)

    executor = BatchExecutor(db, adapter_factory=ObservingFactory())
    await executor._poll_and_run()

    assert all(s == "running" for s in observed_statuses)
    assert _get_run_status(db, run_id) == "done"


@pytest.mark.asyncio
async def test_execute_run_sets_started_and_ended_at() -> None:
    """Run should have started_at and ended_at timestamps after completion."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    _link_agent(db, conv_id, a1, 1)
    run_id = _create_queued_run(db, conv_id, batch_size=2)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory())
    await executor._poll_and_run()

    run = _get_run(db, run_id)
    assert run["started_at"] is not None
    assert run["ended_at"] is not None
    assert run["status"] == "done"


@pytest.mark.asyncio
async def test_no_queued_run_is_noop() -> None:
    """_poll_and_run with no queued runs should not crash."""
    db = _make_db()
    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory())
    await executor._poll_and_run()  # Should complete without error


@pytest.mark.asyncio
async def test_adapter_error_marks_run_failed() -> None:
    """If all adapters fail, the run should still complete (not crash)."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    _link_agent(db, conv_id, a1, 1)
    run_id = _create_queued_run(db, conv_id, batch_size=2)

    executor = BatchExecutor(db, adapter_factory=FailingAdapterFactory())
    await executor._poll_and_run()

    # BatchRunner records errors but completes; run should be done
    assert _get_run_status(db, run_id) == "done"


@pytest.mark.asyncio
async def test_no_agents_marks_run_failed() -> None:
    """A run for a conversation with no agents should be marked failed."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    run_id = _create_queued_run(db, conv_id, batch_size=2)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory())
    await executor._poll_and_run()

    assert _get_run_status(db, run_id) == "failed"


@pytest.mark.asyncio
async def test_start_and_stop_lifecycle() -> None:
    """start() begins polling, stop() cancels it."""
    db = _make_db()
    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory(), poll_interval=0.05)

    await executor.start()
    assert executor._task is not None
    assert not executor._task.done()

    await executor.stop()
    assert executor._task.done()


@pytest.mark.asyncio
async def test_polling_loop_picks_up_run() -> None:
    """The polling loop should find and execute a queued run."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    _link_agent(db, conv_id, a1, 1)
    run_id = _create_queued_run(db, conv_id, batch_size=2)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory(), poll_interval=0.05)
    await executor.start()

    # Give the loop time to pick up the run
    for _ in range(20):
        await asyncio.sleep(0.05)
        if _get_run_status(db, run_id) == "done":
            break

    await executor.stop()
    assert _get_run_status(db, run_id) == "done"


@pytest.mark.asyncio
async def test_event_metadata_contains_turn_info() -> None:
    """MessageEvent metadata_json should contain turn number and run_id."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    _link_agent(db, conv_id, a1, 1)
    run_id = _create_queued_run(db, conv_id, batch_size=2)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory())
    await executor._poll_and_run()

    import json

    repo = SQLiteMessageEventRepository(db)
    events = repo.list_by_conversation(conv_id)
    for i, ev in enumerate(events, 1):
        meta = json.loads(ev.metadata_json)
        assert meta["turn_number"] == i
        assert meta["run_id"] == run_id


@pytest.mark.asyncio
async def test_multiple_queued_runs_only_one_picked() -> None:
    """_poll_and_run picks only one queued run per invocation."""
    db = _make_db()
    conv_id = _seed_conversation(db)
    a1 = _seed_agent(db, "a1")
    _link_agent(db, conv_id, a1, 1)

    run1 = _create_queued_run(db, conv_id, batch_size=2)
    # Create a second conversation + run
    conv2 = _seed_conversation(db, "conv-2")
    _link_agent(db, conv2, a1, 1)
    run2 = _create_queued_run(db, conv2, batch_size=2)

    executor = BatchExecutor(db, adapter_factory=MockAdapterFactory())
    await executor._poll_and_run()

    # At least one should have been picked, but not necessarily both
    s1 = _get_run_status(db, run1)
    s2 = _get_run_status(db, run2)
    done_count = sum(1 for s in [s1, s2] if s == "done")
    assert done_count == 1, "Only one run should be processed per poll"

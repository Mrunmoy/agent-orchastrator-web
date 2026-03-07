"""Tests for adapter output normalization."""

from __future__ import annotations

from datetime import UTC, datetime

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus
from agent_orchestrator.adapters.normalize import (
    normalize,
    normalize_batch,
)


def test_normalize_idle_maps_to_ok():
    result = AdapterResult(text="hello", status=AdapterStatus.IDLE)
    msg = normalize(result, agent_id="a1")
    assert msg.status == "ok"


def test_normalize_timed_out_maps_to_timeout():
    result = AdapterResult(text="hello", status=AdapterStatus.TIMED_OUT)
    msg = normalize(result, agent_id="a1")
    assert msg.status == "timeout"


def test_normalize_error_maps_to_error():
    result = AdapterResult(text="hello", status=AdapterStatus.ERROR)
    msg = normalize(result, agent_id="a1")
    assert msg.status == "error"


def test_normalize_running_maps_to_ok():
    result = AdapterResult(text="hello", status=AdapterStatus.RUNNING)
    msg = normalize(result, agent_id="a1")
    assert msg.status == "ok"


def test_text_is_stripped():
    result = AdapterResult(text="  hello world  \n")
    msg = normalize(result, agent_id="a1")
    assert msg.text == "hello world"


def test_token_count_is_word_count():
    result = AdapterResult(text="one two three four")
    msg = normalize(result, agent_id="a1")
    assert msg.token_count == 4


def test_auto_generated_timestamp_when_none():
    result = AdapterResult(text="hi")
    before = datetime.now(UTC)
    msg = normalize(result, agent_id="a1")
    after = datetime.now(UTC)
    ts = datetime.fromisoformat(msg.timestamp)
    assert before <= ts <= after


def test_explicit_timestamp_is_used():
    result = AdapterResult(text="hi")
    ts = "2026-01-15T12:00:00+00:00"
    msg = normalize(result, agent_id="a1", timestamp=ts)
    assert msg.timestamp == ts


def test_session_id_carried_over():
    result = AdapterResult(text="hi", session_id="sess-42")
    msg = normalize(result, agent_id="a1")
    assert msg.session_id == "sess-42"


def test_metadata_carried_over():
    result = AdapterResult(text="hi", metadata={"model": "gpt-4"})
    msg = normalize(result, agent_id="a1")
    assert msg.metadata == {"model": "gpt-4"}


def test_agent_id_set():
    result = AdapterResult(text="hi")
    msg = normalize(result, agent_id="claude-1")
    assert msg.agent_id == "claude-1"


def test_normalize_batch_processes_multiple():
    results = [
        ("a1", AdapterResult(text="one", status=AdapterStatus.IDLE)),
        ("a2", AdapterResult(text="two", status=AdapterStatus.ERROR)),
    ]
    msgs = normalize_batch(results)
    assert len(msgs) == 2
    assert msgs[0].agent_id == "a1"
    assert msgs[0].status == "ok"
    assert msgs[1].agent_id == "a2"
    assert msgs[1].status == "error"


def test_normalize_batch_shared_timestamp():
    results = [
        ("a1", AdapterResult(text="one")),
        ("a2", AdapterResult(text="two")),
    ]
    ts = "2026-01-15T12:00:00+00:00"
    msgs = normalize_batch(results, timestamp=ts)
    assert all(m.timestamp == ts for m in msgs)

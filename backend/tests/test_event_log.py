"""Tests for JSONL event log writer/reader (DATA-003)."""

from __future__ import annotations

import json
from pathlib import Path

from agent_orchestrator.storage.event_log import (
    EventLogReader,
    EventLogWriter,
    conversation_log_path,
    scheduler_log_path,
)

# ---------------------------------------------------------------------------
# Writer: file and directory creation
# ---------------------------------------------------------------------------


def test_writer_creates_file_and_parent_dirs(tmp_path: Path) -> None:
    log = tmp_path / "nested" / "deep" / "events.jsonl"
    writer = EventLogWriter(log)
    writer.append({"event_id": "e1", "event_type": "test", "payload": {}})
    writer.close()
    assert log.exists()


def test_writer_accepts_path_object(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    writer = EventLogWriter(log)  # Path, not str
    writer.append({"event_id": "e1", "event_type": "test", "payload": {}})
    writer.close()
    assert log.exists()


def test_writer_accepts_string_path(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    writer = EventLogWriter(str(log))  # str path
    writer.append({"event_id": "e1", "event_type": "test", "payload": {}})
    writer.close()
    assert log.exists()


# ---------------------------------------------------------------------------
# Writer: append() produces valid JSON lines
# ---------------------------------------------------------------------------


def test_append_writes_valid_json_line(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        w.append({"event_id": "e1", "event_type": "test", "payload": {"k": "v"}})
    line = log.read_text().strip()
    obj = json.loads(line)
    assert obj["event_id"] == "e1"
    assert obj["event_type"] == "test"
    assert obj["payload"] == {"k": "v"}


def test_append_adds_timestamp_if_missing(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        w.append({"event_id": "e1", "event_type": "test", "payload": {}})
    obj = json.loads(log.read_text().strip())
    assert "timestamp" in obj
    # Should be ISO format with UTC timezone indicator
    assert obj["timestamp"].endswith("+00:00") or obj["timestamp"].endswith("Z")


def test_append_preserves_existing_timestamp(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    ts = "2026-01-15T10:30:00+00:00"
    with EventLogWriter(log) as w:
        w.append({"event_id": "e1", "event_type": "test", "payload": {}, "timestamp": ts})
    obj = json.loads(log.read_text().strip())
    assert obj["timestamp"] == ts


def test_multiple_appends_produce_multiple_lines(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        for i in range(5):
            w.append({"event_id": f"e{i}", "event_type": "test", "payload": {}})
    lines = [ln for ln in log.read_text().splitlines() if ln.strip()]
    assert len(lines) == 5
    for i, line in enumerate(lines):
        obj = json.loads(line)
        assert obj["event_id"] == f"e{i}"


# ---------------------------------------------------------------------------
# Writer: atomicity (flush after each write)
# ---------------------------------------------------------------------------


def test_append_flushes_after_each_write(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    writer = EventLogWriter(log)
    writer.append({"event_id": "e1", "event_type": "test", "payload": {}})
    # Without closing, data should already be on disk
    content = log.read_text()
    assert "e1" in content
    writer.close()


# ---------------------------------------------------------------------------
# Writer: context manager
# ---------------------------------------------------------------------------


def test_context_manager_opens_and_closes(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        w.append({"event_id": "e1", "event_type": "test", "payload": {}})
    # After exiting, the writer should be closed; file should exist
    assert log.exists()
    # Verify we can still read the file (not locked)
    data = json.loads(log.read_text().strip())
    assert data["event_id"] == "e1"


# ---------------------------------------------------------------------------
# Reader: read_all()
# ---------------------------------------------------------------------------


def test_reader_read_all_returns_all_events(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        for i in range(3):
            w.append({"event_id": f"e{i}", "event_type": "test", "payload": {}})
    reader = EventLogReader(log)
    events = reader.read_all()
    assert len(events) == 3
    assert [e["event_id"] for e in events] == ["e0", "e1", "e2"]


# ---------------------------------------------------------------------------
# Reader: read_since()
# ---------------------------------------------------------------------------


def test_reader_read_since_filters_correctly(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        for i in range(5):
            w.append({"event_id": f"e{i}", "event_type": "test", "payload": {}})
    reader = EventLogReader(log)
    events = reader.read_since("e2")
    assert len(events) == 2
    assert [e["event_id"] for e in events] == ["e3", "e4"]


def test_reader_read_since_unknown_id_returns_all(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        w.append({"event_id": "e0", "event_type": "test", "payload": {}})
    reader = EventLogReader(log)
    events = reader.read_since("nonexistent")
    assert len(events) == 1


# ---------------------------------------------------------------------------
# Reader: tail()
# ---------------------------------------------------------------------------


def test_reader_tail_returns_last_n_events(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        for i in range(10):
            w.append({"event_id": f"e{i}", "event_type": "test", "payload": {}})
    reader = EventLogReader(log)
    events = reader.tail(3)
    assert len(events) == 3
    assert [e["event_id"] for e in events] == ["e7", "e8", "e9"]


def test_reader_tail_returns_all_if_fewer_than_n(tmp_path: Path) -> None:
    log = tmp_path / "events.jsonl"
    with EventLogWriter(log) as w:
        w.append({"event_id": "e0", "event_type": "test", "payload": {}})
    reader = EventLogReader(log)
    events = reader.tail(10)
    assert len(events) == 1


# ---------------------------------------------------------------------------
# Reader: non-existent file
# ---------------------------------------------------------------------------


def test_reader_returns_empty_list_for_nonexistent_file(tmp_path: Path) -> None:
    reader = EventLogReader(tmp_path / "nope.jsonl")
    assert reader.read_all() == []
    assert reader.read_since("x") == []
    assert reader.tail(5) == []


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def test_conversation_log_path_returns_correct_path() -> None:
    p = conversation_log_path("conv-abc-123")
    assert p == Path("data/transcripts/conv-abc-123.jsonl")


def test_scheduler_log_path_returns_correct_path() -> None:
    p = scheduler_log_path()
    assert p == Path("data/audit/scheduler.jsonl")

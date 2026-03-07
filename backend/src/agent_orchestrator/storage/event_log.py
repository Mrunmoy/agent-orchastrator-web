"""Append-only JSONL event log writer and reader (DATA-003).

Provides EventLogWriter for atomic, append-only JSONL writes and
EventLogReader for reading/filtering events from JSONL files.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import IO


class EventLogWriter:
    """Append-only writer for JSONL event log files.

    Creates parent directories on init. Each ``append()`` call writes a
    single JSON line and flushes immediately for crash safety.
    """

    def __init__(self, log_path: str | Path) -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: IO[str] | None = self._path.open("a", encoding="utf-8")

    def append(self, event: dict) -> None:
        """Append *event* as a single JSON line.

        Adds an ISO-8601 UTC ``timestamp`` field if not already present.
        Flushes to disk after every write.
        """
        if self._fh is None:
            raise RuntimeError("Writer is closed")
        if "timestamp" not in event:
            event = {
                **event,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        self._fh.write(json.dumps(event, separators=(",", ":")) + "\n")
        self._fh.flush()

    def close(self) -> None:
        """Close the underlying file handle."""
        if self._fh is not None:
            self._fh.close()
            self._fh = None

    # -- context manager -----------------------------------------------------

    def __enter__(self) -> EventLogWriter:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.close()


class EventLogReader:
    """Stateless reader for JSONL event log files.

    All read methods return an empty list when the file does not exist.
    """

    def __init__(self, log_path: str | Path) -> None:
        self._path = Path(log_path)

    def read_all(self) -> list[dict]:
        """Return every event in the log, in order."""
        if not self._path.exists():
            return []
        events: list[dict] = []
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped:
                    events.append(json.loads(stripped))
        return events

    def read_since(self, event_id: str) -> list[dict]:
        """Return events that appear *after* the line with *event_id*.

        If *event_id* is not found, all events are returned.
        """
        all_events = self.read_all()
        for idx, ev in enumerate(all_events):
            if ev.get("event_id") == event_id:
                return all_events[idx + 1 :]
        return all_events

    def tail(self, n: int = 10) -> list[dict]:
        """Return the last *n* events."""
        all_events = self.read_all()
        return all_events[-n:]


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def conversation_log_path(conversation_id: str) -> Path:
    """Return the canonical JSONL log path for a conversation."""
    return Path("data/transcripts") / f"{conversation_id}.jsonl"


def scheduler_log_path() -> Path:
    """Return the canonical JSONL log path for the scheduler audit log."""
    return Path("data/audit/scheduler.jsonl")

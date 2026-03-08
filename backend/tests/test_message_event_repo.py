"""Tests for SQLiteMessageEventRepository (T-108).

TDD test suite covering append, get_by_event_id, list_by_conversation
(with pagination), list_by_type, and append-only enforcement.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from agent_orchestrator.orchestrator.models import EventType, MessageEvent
from agent_orchestrator.storage.db import DatabaseManager
from agent_orchestrator.storage.repositories.sqlite_message_event import (
    SQLiteMessageEventRepository,
)


def _make_event(
    conversation_id: str = "conv-1",
    source_type: str = "agent",
    text: str = "hello",
    event_type: str = EventType.CHAT_MESSAGE.value,
    source_id: str | None = "agent-1",
    metadata_json: str = "{}",
) -> MessageEvent:
    """Create a MessageEvent with a fresh UUID and timestamp."""
    return MessageEvent(
        conversation_id=conversation_id,
        event_id=str(uuid.uuid4()),
        source_type=source_type,
        text=text,
        event_type=event_type,
        created_at=datetime.now(timezone.utc).isoformat(),
        source_id=source_id,
        metadata_json=metadata_json,
    )


_NOW = "2026-03-07T00:00:00Z"


def _seed_data(db: DatabaseManager) -> None:
    """Insert conversation and agent rows referenced by FK constraints."""
    with db.connection() as conn:
        for cid in ("conv-1", "conv-2", "conv-42"):
            conn.execute(
                "INSERT OR IGNORE INTO conversation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, "Conv", "/tmp", "debate", "design_debate", "open", 100, 1, None, None, _NOW, _NOW, None),
            )
        for aid in ("agent-1", "user-1"):
            conn.execute(
                "INSERT OR IGNORE INTO agent VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (aid, aid, "claude", "opus-4", None, "worker", "idle", None, "[]", 0, _NOW, _NOW),
            )
        conn.commit()


@pytest.fixture()
def repo() -> SQLiteMessageEventRepository:
    """Return a repository backed by a fresh in-memory database."""
    db = DatabaseManager(":memory:")
    db.initialize()
    _seed_data(db)
    return SQLiteMessageEventRepository(db)


# ── TT-108-01: append creates message_event with unique UUID event_id ────────


class TestAppend:
    def test_returns_event_with_autoincrement_id(
        self, repo: SQLiteMessageEventRepository
    ):
        event = _make_event()
        result = repo.append(event)
        assert result.id is not None
        assert isinstance(result.id, int)
        assert result.id > 0

    def test_preserves_event_id(self, repo: SQLiteMessageEventRepository):
        event = _make_event()
        result = repo.append(event)
        assert result.event_id == event.event_id
        assert len(result.event_id) == 36  # UUID format

    def test_unique_event_ids(self, repo: SQLiteMessageEventRepository):
        e1 = repo.append(_make_event())
        e2 = repo.append(_make_event())
        assert e1.event_id != e2.event_id

    def test_preserves_all_fields(self, repo: SQLiteMessageEventRepository):
        event = _make_event(
            conversation_id="conv-42",
            source_type="user",
            text="test message",
            event_type=EventType.STEER.value,
            source_id="user-1",
            metadata_json='{"key": "value"}',
        )
        result = repo.append(event)
        assert result.conversation_id == "conv-42"
        assert result.source_type == "user"
        assert result.text == "test message"
        assert result.event_type == EventType.STEER.value
        assert result.source_id == "user-1"
        assert result.metadata_json == '{"key": "value"}'

    def test_get_by_event_id_returns_appended(
        self, repo: SQLiteMessageEventRepository
    ):
        event = _make_event()
        appended = repo.append(event)
        fetched = repo.get_by_event_id(appended.event_id)
        assert fetched is not None
        assert fetched.event_id == appended.event_id
        assert fetched.text == appended.text

    def test_get_by_event_id_returns_none_for_missing(
        self, repo: SQLiteMessageEventRepository
    ):
        assert repo.get_by_event_id("nonexistent") is None

    def test_source_id_nullable(self, repo: SQLiteMessageEventRepository):
        event = _make_event(source_id=None)
        result = repo.append(event)
        assert result.source_id is None


# ── TT-108-02: list_by_conversation with offset returns paginated events ─────


class TestListByConversation:
    def test_returns_events_for_conversation(
        self, repo: SQLiteMessageEventRepository
    ):
        repo.append(_make_event(conversation_id="conv-1", text="msg1"))
        repo.append(_make_event(conversation_id="conv-1", text="msg2"))
        repo.append(_make_event(conversation_id="conv-2", text="other"))

        events = repo.list_by_conversation("conv-1")
        assert len(events) == 2
        assert all(e.conversation_id == "conv-1" for e in events)

    def test_ordered_by_id_ascending(
        self, repo: SQLiteMessageEventRepository
    ):
        repo.append(_make_event(text="first"))
        repo.append(_make_event(text="second"))
        repo.append(_make_event(text="third"))

        events = repo.list_by_conversation("conv-1")
        assert [e.text for e in events] == ["first", "second", "third"]

    def test_limit(self, repo: SQLiteMessageEventRepository):
        for i in range(5):
            repo.append(_make_event(text=f"msg-{i}"))

        events = repo.list_by_conversation("conv-1", limit=3)
        assert len(events) == 3
        assert [e.text for e in events] == ["msg-0", "msg-1", "msg-2"]

    def test_offset(self, repo: SQLiteMessageEventRepository):
        for i in range(5):
            repo.append(_make_event(text=f"msg-{i}"))

        events = repo.list_by_conversation("conv-1", offset=2)
        assert len(events) == 3
        assert [e.text for e in events] == ["msg-2", "msg-3", "msg-4"]

    def test_limit_and_offset(self, repo: SQLiteMessageEventRepository):
        for i in range(5):
            repo.append(_make_event(text=f"msg-{i}"))

        events = repo.list_by_conversation("conv-1", limit=2, offset=1)
        assert len(events) == 2
        assert [e.text for e in events] == ["msg-1", "msg-2"]

    def test_empty_conversation(self, repo: SQLiteMessageEventRepository):
        events = repo.list_by_conversation("nonexistent")
        assert events == []


# ── TT-108-03: list_by_type filters to specified event_type ──────────────────


class TestListByType:
    def test_filters_by_event_type(self, repo: SQLiteMessageEventRepository):
        repo.append(
            _make_event(event_type=EventType.CHAT_MESSAGE.value, text="chat")
        )
        repo.append(
            _make_event(event_type=EventType.STEER.value, text="steer")
        )
        repo.append(
            _make_event(
                event_type=EventType.CHAT_MESSAGE.value, text="chat2"
            )
        )

        chats = repo.list_by_type("conv-1", EventType.CHAT_MESSAGE.value)
        assert len(chats) == 2
        assert all(
            e.event_type == EventType.CHAT_MESSAGE.value for e in chats
        )

    def test_scoped_to_conversation(
        self, repo: SQLiteMessageEventRepository
    ):
        repo.append(
            _make_event(
                conversation_id="conv-1",
                event_type=EventType.STEER.value,
            )
        )
        repo.append(
            _make_event(
                conversation_id="conv-2",
                event_type=EventType.STEER.value,
            )
        )

        steers = repo.list_by_type("conv-1", EventType.STEER.value)
        assert len(steers) == 1
        assert steers[0].conversation_id == "conv-1"

    def test_returns_empty_for_no_matches(
        self, repo: SQLiteMessageEventRepository
    ):
        repo.append(
            _make_event(event_type=EventType.CHAT_MESSAGE.value)
        )
        result = repo.list_by_type("conv-1", EventType.PHASE_CHANGE.value)
        assert result == []


# ── TT-108-04: No update or delete methods exist (append-only enforcement) ───


class TestAppendOnly:
    def test_no_update_method(self, repo: SQLiteMessageEventRepository):
        assert not hasattr(repo, "update")

    def test_no_delete_method(self, repo: SQLiteMessageEventRepository):
        assert not hasattr(repo, "delete")

    def test_no_soft_delete_method(self, repo: SQLiteMessageEventRepository):
        assert not hasattr(repo, "soft_delete")

    def test_no_remove_method(self, repo: SQLiteMessageEventRepository):
        assert not hasattr(repo, "remove")

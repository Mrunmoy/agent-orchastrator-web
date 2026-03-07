"""Tests for the notification pipeline (COORD-003)."""

from __future__ import annotations

import uuid

from agent_orchestrator.runtime.notifications import (
    LoggingHandler,
    Notification,
    NotificationPipeline,
    NotificationType,
)

# ---------------------------------------------------------------------------
# NotificationType enum
# ---------------------------------------------------------------------------


class TestNotificationType:
    def test_values(self):
        assert NotificationType.NEEDS_INPUT == "needs_input"
        assert NotificationType.BLOCKED == "blocked"
        assert NotificationType.COMPLETED == "completed"
        assert NotificationType.QUEUED == "queued"
        assert NotificationType.ERROR == "error"

    def test_is_str_enum(self):
        assert isinstance(NotificationType.NEEDS_INPUT, str)


# ---------------------------------------------------------------------------
# Notification dataclass
# ---------------------------------------------------------------------------


class TestNotification:
    def test_defaults(self):
        n = Notification(
            id="abc",
            notification_type=NotificationType.COMPLETED,
            conversation_id="conv-1",
            message="done",
            created_at="2026-01-01T00:00:00Z",
        )
        assert n.read is False
        assert n.metadata is None

    def test_with_metadata(self):
        n = Notification(
            id="abc",
            notification_type=NotificationType.ERROR,
            conversation_id="conv-1",
            message="oops",
            created_at="2026-01-01T00:00:00Z",
            metadata={"detail": "stack trace"},
        )
        assert n.metadata == {"detail": "stack trace"}


# ---------------------------------------------------------------------------
# LoggingHandler
# ---------------------------------------------------------------------------


class TestLoggingHandler:
    def test_stores_notifications(self):
        handler = LoggingHandler()
        n = Notification(
            id="1",
            notification_type=NotificationType.QUEUED,
            conversation_id="c1",
            message="queued",
            created_at="2026-01-01T00:00:00Z",
        )
        handler.handle(n)
        assert len(handler.notifications) == 1
        assert handler.notifications[0] is n

    def test_multiple_notifications(self):
        handler = LoggingHandler()
        for i in range(3):
            handler.handle(
                Notification(
                    id=str(i),
                    notification_type=NotificationType.COMPLETED,
                    conversation_id="c1",
                    message=f"msg-{i}",
                    created_at="2026-01-01T00:00:00Z",
                )
            )
        assert len(handler.notifications) == 3


# ---------------------------------------------------------------------------
# NotificationPipeline
# ---------------------------------------------------------------------------


class TestPipelineEmit:
    def test_emit_creates_notification_with_correct_fields(self):
        pipeline = NotificationPipeline()
        n = pipeline.emit(NotificationType.NEEDS_INPUT, "conv-42", "User input required")
        assert n.notification_type == NotificationType.NEEDS_INPUT
        assert n.conversation_id == "conv-42"
        assert n.message == "User input required"
        assert n.read is False
        assert n.metadata is None
        # id should be a valid UUID
        uuid.UUID(n.id)
        # created_at should be an ISO timestamp string
        assert isinstance(n.created_at, str)
        assert "T" in n.created_at

    def test_emit_with_metadata(self):
        pipeline = NotificationPipeline()
        meta = {"key": "value"}
        n = pipeline.emit(NotificationType.ERROR, "conv-1", "boom", metadata=meta)
        assert n.metadata == meta

    def test_emit_dispatches_to_all_handlers(self):
        pipeline = NotificationPipeline()
        h1 = LoggingHandler()
        h2 = LoggingHandler()
        pipeline.add_handler(h1)
        pipeline.add_handler(h2)

        pipeline.emit(NotificationType.COMPLETED, "c1", "done")
        assert len(h1.notifications) == 1
        assert len(h2.notifications) == 1

    def test_emit_multiple_types(self):
        pipeline = NotificationPipeline()
        n1 = pipeline.emit(NotificationType.NEEDS_INPUT, "c1", "a")
        n2 = pipeline.emit(NotificationType.BLOCKED, "c2", "b")
        n3 = pipeline.emit(NotificationType.COMPLETED, "c3", "c")
        n4 = pipeline.emit(NotificationType.QUEUED, "c4", "d")
        n5 = pipeline.emit(NotificationType.ERROR, "c5", "e")
        assert n1.notification_type == NotificationType.NEEDS_INPUT
        assert n2.notification_type == NotificationType.BLOCKED
        assert n3.notification_type == NotificationType.COMPLETED
        assert n4.notification_type == NotificationType.QUEUED
        assert n5.notification_type == NotificationType.ERROR


class TestPipelineHistory:
    def test_history_returns_all(self):
        pipeline = NotificationPipeline()
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        pipeline.emit(NotificationType.BLOCKED, "c2", "b")
        assert len(pipeline.history()) == 2

    def test_history_empty_initially(self):
        pipeline = NotificationPipeline()
        assert pipeline.history() == []


class TestPipelineUnread:
    def test_unread_filters_correctly(self):
        pipeline = NotificationPipeline()
        n1 = pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        pipeline.emit(NotificationType.BLOCKED, "c2", "b")
        pipeline.mark_read(n1.id)
        unread = pipeline.unread()
        assert len(unread) == 1
        assert unread[0].conversation_id == "c2"

    def test_unread_all_when_none_read(self):
        pipeline = NotificationPipeline()
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        pipeline.emit(NotificationType.BLOCKED, "c2", "b")
        assert len(pipeline.unread()) == 2


class TestPipelineMarkRead:
    def test_mark_read_single(self):
        pipeline = NotificationPipeline()
        n = pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        assert pipeline.mark_read(n.id) is True
        assert n.read is True

    def test_mark_read_nonexistent_returns_false(self):
        pipeline = NotificationPipeline()
        assert pipeline.mark_read("no-such-id") is False

    def test_mark_all_read(self):
        pipeline = NotificationPipeline()
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        pipeline.emit(NotificationType.BLOCKED, "c2", "b")
        pipeline.emit(NotificationType.QUEUED, "c3", "c")
        count = pipeline.mark_all_read()
        assert count == 3
        assert len(pipeline.unread()) == 0

    def test_mark_all_read_returns_zero_when_already_read(self):
        pipeline = NotificationPipeline()
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        pipeline.mark_all_read()
        assert pipeline.mark_all_read() == 0


class TestPipelineClear:
    def test_clear_removes_all(self):
        pipeline = NotificationPipeline()
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        pipeline.emit(NotificationType.BLOCKED, "c2", "b")
        pipeline.clear()
        assert pipeline.history() == []
        assert pipeline.unread() == []


class TestPipelineHandlers:
    def test_add_handler(self):
        pipeline = NotificationPipeline()
        h = LoggingHandler()
        pipeline.add_handler(h)
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        assert len(h.notifications) == 1

    def test_remove_handler(self):
        pipeline = NotificationPipeline()
        h = LoggingHandler()
        pipeline.add_handler(h)
        pipeline.remove_handler(h)
        pipeline.emit(NotificationType.COMPLETED, "c1", "a")
        assert len(h.notifications) == 0

    def test_remove_handler_not_added(self):
        pipeline = NotificationPipeline()
        h = LoggingHandler()
        # Should not raise
        pipeline.remove_handler(h)


class TestCustomHandler:
    def test_custom_handler_protocol(self):
        """A plain class with handle() should work as a handler."""

        class Counter:
            def __init__(self):
                self.count = 0

            def handle(self, notification: Notification) -> None:
                self.count += 1

        pipeline = NotificationPipeline()
        c = Counter()
        pipeline.add_handler(c)  # type: ignore[arg-type]
        pipeline.emit(NotificationType.QUEUED, "c1", "q")
        assert c.count == 1

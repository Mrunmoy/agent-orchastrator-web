"""Notification pipeline for orchestration events (COORD-003).

Emits notifications for Needs Input, Blocked, Completed, Queued, and Error
events and dispatches them to pluggable handlers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------


class NotificationType(str, Enum):
    """Types of notification events the pipeline can emit."""

    NEEDS_INPUT = "needs_input"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    QUEUED = "queued"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Notification:
    """A single notification record."""

    id: str
    notification_type: NotificationType
    conversation_id: str
    message: str
    created_at: str
    read: bool = False
    metadata: dict | None = None


# ---------------------------------------------------------------------------
# Handler protocol & built-in handler
# ---------------------------------------------------------------------------


@runtime_checkable
class NotificationHandler(Protocol):
    """Interface that notification consumers must satisfy."""

    def handle(self, notification: Notification) -> None: ...


class LoggingHandler:
    """Stores notifications in an internal list for later retrieval."""

    def __init__(self) -> None:
        self._notifications: list[Notification] = []

    def handle(self, notification: Notification) -> None:
        self._notifications.append(notification)

    @property
    def notifications(self) -> list[Notification]:
        return list(self._notifications)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class NotificationPipeline:
    """Central hub that creates, dispatches, and tracks notifications."""

    def __init__(self) -> None:
        self._handlers: list[NotificationHandler] = []
        self._history: list[Notification] = []

    # -- handler management --------------------------------------------------

    def add_handler(self, handler: NotificationHandler) -> None:
        self._handlers.append(handler)

    def remove_handler(self, handler: NotificationHandler) -> None:
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    # -- emit ----------------------------------------------------------------

    def emit(
        self,
        notification_type: NotificationType,
        conversation_id: str,
        message: str,
        metadata: dict | None = None,
    ) -> Notification:
        notification = Notification(
            id=str(uuid.uuid4()),
            notification_type=notification_type,
            conversation_id=conversation_id,
            message=message,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
        self._history.append(notification)
        for handler in self._handlers:
            handler.handle(notification)
        return notification

    # -- query ---------------------------------------------------------------

    def history(self) -> list[Notification]:
        return list(self._history)

    def unread(self) -> list[Notification]:
        return [n for n in self._history if not n.read]

    # -- mutation ------------------------------------------------------------

    def mark_read(self, notification_id: str) -> bool:
        for n in self._history:
            if n.id == notification_id:
                n.read = True
                return True
        return False

    def mark_all_read(self) -> int:
        count = 0
        for n in self._history:
            if not n.read:
                n.read = True
                count += 1
        return count

    def clear(self) -> None:
        self._history.clear()

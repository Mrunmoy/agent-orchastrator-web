"""Steering note injection between run windows (ORCH-005).

Allows users to inject guidance notes that modify agent behavior
between batch windows.  The :class:`SteeringManager` accumulates notes
per conversation and builds a prompt prefix consumed by the batch runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class SteeringNote:
    """A single user-supplied steering note."""

    conversation_id: str
    note_text: str
    injected_at: str
    applied: bool = False


class SteeringManager:
    """Manage steering notes for a single conversation."""

    def __init__(self, conversation_id: str) -> None:
        self._conversation_id = conversation_id
        self._notes: list[SteeringNote] = []

    # -- Public API ----------------------------------------------------------

    def add_note(self, text: str) -> SteeringNote:
        """Add a new steering note and return it."""
        note = SteeringNote(
            conversation_id=self._conversation_id,
            note_text=text,
            injected_at=datetime.now(UTC).isoformat(),
        )
        self._notes.append(note)
        return note

    def pending_notes(self) -> list[SteeringNote]:
        """Return all unapplied notes."""
        return [n for n in self._notes if not n.applied]

    def apply_notes(self) -> list[SteeringNote]:
        """Mark all pending notes as applied and return them."""
        pending = self.pending_notes()
        for note in pending:
            note.applied = True
        return pending

    def build_prompt_prefix(self) -> str:
        """Build a prompt prefix from pending notes.

        Returns an empty string when there are no pending notes.
        """
        pending = self.pending_notes()
        if not pending:
            return ""
        lines = "".join(f"- {n.note_text}\n" for n in pending)
        return "[Steering] The user has provided the following guidance:\n" f"{lines}"

    def clear(self) -> None:
        """Remove all notes (applied and pending)."""
        self._notes.clear()

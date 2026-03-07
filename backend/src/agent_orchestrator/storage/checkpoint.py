"""Checkpoint pack builder for conversation resume (DATA-004).

Builds compact context summaries so conversations can resume without
replaying full transcripts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from agent_orchestrator.storage.event_log import EventLogReader, conversation_log_path


@dataclass
class CheckpointPack:
    """Compact context summary for conversation resume."""

    conversation_id: str
    summary: str
    key_decisions: list[str]
    recent_events: list[dict]  # last N events from the log
    token_estimate: int
    created_at: str  # ISO-8601 UTC


class CheckpointBuilder:
    """Builds and compacts CheckpointPack instances."""

    def __init__(
        self,
        conversation_id: str,
        *,
        max_recent_events: int = 20,
        max_token_estimate: int = 4000,
    ) -> None:
        self.conversation_id = conversation_id
        self.max_recent_events = max_recent_events
        self.max_token_estimate = max_token_estimate

    def build(
        self,
        summary: str,
        key_decisions: list[str],
        events: list[dict] | None = None,
        log_path: str | Path | None = None,
    ) -> CheckpointPack:
        """Create a CheckpointPack from summary, decisions, and events.

        If *events* is None, reads from the JSONL log using EventLogReader.
        *log_path* overrides the default conversation log path when provided.
        """
        if events is None:
            path = Path(log_path) if log_path else conversation_log_path(self.conversation_id)
            reader = EventLogReader(path)
            events = reader.read_all()

        recent = events[-self.max_recent_events :]

        all_text = self._pack_text(summary, key_decisions, recent)
        token_estimate = self.estimate_tokens(all_text)

        return CheckpointPack(
            conversation_id=self.conversation_id,
            summary=summary,
            key_decisions=key_decisions,
            recent_events=recent,
            token_estimate=token_estimate,
            created_at=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimate: word count * 1.3, rounded to int."""
        words = text.split()
        if not words:
            return 0
        return round(len(words) * 1.3)

    def compact(self, pack: CheckpointPack) -> CheckpointPack:
        """Trim recent_events and/or summary to stay within max_token_estimate.

        First reduces recent_events (dropping oldest first). If still over
        budget, truncates the summary to fit. Returns a new CheckpointPack.
        """
        if pack.token_estimate <= self.max_token_estimate:
            return pack

        summary = pack.summary
        key_decisions = pack.key_decisions
        recent_events = list(pack.recent_events)

        # Phase 1: drop oldest events one at a time
        while recent_events:
            all_text = self._pack_text(summary, key_decisions, recent_events)
            est = self.estimate_tokens(all_text)
            if est <= self.max_token_estimate:
                return CheckpointPack(
                    conversation_id=pack.conversation_id,
                    summary=summary,
                    key_decisions=key_decisions,
                    recent_events=recent_events,
                    token_estimate=est,
                    created_at=pack.created_at,
                )
            recent_events.pop(0)

        # Phase 2: truncate summary
        all_text = self._pack_text(summary, key_decisions, [])
        est = self.estimate_tokens(all_text)
        if est <= self.max_token_estimate:
            return CheckpointPack(
                conversation_id=pack.conversation_id,
                summary=summary,
                key_decisions=key_decisions,
                recent_events=[],
                token_estimate=est,
                created_at=pack.created_at,
            )

        # Progressively shorten summary by words
        words = summary.split()
        while words:
            words.pop()
            candidate = " ".join(words)
            all_text = self._pack_text(candidate, key_decisions, [])
            est = self.estimate_tokens(all_text)
            if est <= self.max_token_estimate:
                return CheckpointPack(
                    conversation_id=pack.conversation_id,
                    summary=candidate,
                    key_decisions=key_decisions,
                    recent_events=[],
                    token_estimate=est,
                    created_at=pack.created_at,
                )

        # Edge case: everything trimmed
        final_text = self._pack_text("", key_decisions, [])
        return CheckpointPack(
            conversation_id=pack.conversation_id,
            summary="",
            key_decisions=key_decisions,
            recent_events=[],
            token_estimate=self.estimate_tokens(final_text),
            created_at=pack.created_at,
        )

    @staticmethod
    def _pack_text(
        summary: str, key_decisions: list[str], events: list[dict]
    ) -> str:
        """Combine all pack content into a single string for token estimation."""
        parts = [summary]
        parts.extend(key_decisions)
        parts.extend(json.dumps(e) for e in events)
        return " ".join(parts)

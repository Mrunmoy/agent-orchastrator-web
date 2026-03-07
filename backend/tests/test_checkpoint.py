"""Tests for CheckpointBuilder and CheckpointPack (DATA-004)."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from agent_orchestrator.storage.checkpoint import CheckpointBuilder, CheckpointPack
from agent_orchestrator.storage.event_log import EventLogWriter


class TestEstimateTokens:
    def test_basic_word_count(self) -> None:
        result = CheckpointBuilder.estimate_tokens("hello world foo bar")
        # 4 words * 1.3 = 5.2 -> 5
        assert result == 5

    def test_empty_string(self) -> None:
        assert CheckpointBuilder.estimate_tokens("") == 0

    def test_single_word(self) -> None:
        # 1 * 1.3 = 1.3 -> 1
        assert CheckpointBuilder.estimate_tokens("hello") == 1

    def test_ten_words(self) -> None:
        text = " ".join(["word"] * 10)
        # 10 * 1.3 = 13
        assert CheckpointBuilder.estimate_tokens(text) == 13


class TestBuild:
    def test_creates_pack_with_correct_fields(self) -> None:
        builder = CheckpointBuilder("conv-1")
        events = [{"type": "msg", "content": "hi"}]
        pack = builder.build(summary="A summary", key_decisions=["d1"], events=events)

        assert isinstance(pack, CheckpointPack)
        assert pack.conversation_id == "conv-1"
        assert pack.summary == "A summary"
        assert pack.key_decisions == ["d1"]
        assert pack.recent_events == events
        assert isinstance(pack.token_estimate, int)
        assert pack.token_estimate > 0
        # created_at should be a valid ISO-8601 timestamp
        datetime.fromisoformat(pack.created_at)

    def test_uses_provided_events(self) -> None:
        builder = CheckpointBuilder("conv-2")
        events = [{"a": 1}, {"b": 2}, {"c": 3}]
        pack = builder.build(summary="s", key_decisions=[], events=events)
        assert pack.recent_events == events

    def test_limits_to_max_recent_events(self) -> None:
        builder = CheckpointBuilder("conv-3", max_recent_events=3)
        events = [{"i": i} for i in range(10)]
        pack = builder.build(summary="s", key_decisions=[], events=events)
        assert len(pack.recent_events) == 3
        # Should keep the LAST 3
        assert pack.recent_events == events[-3:]

    def test_reads_from_jsonl_when_events_is_none(self, tmp_path) -> None:
        log_file = tmp_path / "conv-read.jsonl"
        with EventLogWriter(log_file) as w:
            w.append({"type": "a", "content": "first"})
            w.append({"type": "b", "content": "second"})

        builder = CheckpointBuilder("conv-read")
        pack = builder.build(
            summary="s",
            key_decisions=[],
            events=None,
            log_path=log_file,
        )
        assert len(pack.recent_events) == 2
        assert pack.recent_events[0]["type"] == "a"
        assert pack.recent_events[1]["type"] == "b"

    def test_token_estimate_is_calculated(self) -> None:
        builder = CheckpointBuilder("conv-4")
        pack = builder.build(
            summary="one two three",
            key_decisions=["alpha beta"],
            events=[{"msg": "hello world"}],
        )
        # Token estimate should cover summary + decisions + events text
        assert pack.token_estimate > 0
        # Verify it roughly matches manual calculation
        all_text = "one two three" + " " + "alpha beta" + " " + json.dumps({"msg": "hello world"})
        expected = CheckpointBuilder.estimate_tokens(all_text)
        assert pack.token_estimate == expected

    def test_created_at_is_utc(self) -> None:
        builder = CheckpointBuilder("conv-5")
        before = datetime.now(UTC)
        pack = builder.build(summary="s", key_decisions=[], events=[])
        after = datetime.now(UTC)
        ts = datetime.fromisoformat(pack.created_at)
        assert before <= ts <= after


class TestCompact:
    def test_returns_same_pack_if_under_limit(self) -> None:
        builder = CheckpointBuilder("c1", max_token_estimate=10000)
        pack = CheckpointPack(
            conversation_id="c1",
            summary="short",
            key_decisions=[],
            recent_events=[],
            token_estimate=10,
            created_at=datetime.now(UTC).isoformat(),
        )
        result = builder.compact(pack)
        assert result.summary == pack.summary
        assert result.recent_events == pack.recent_events
        assert result.token_estimate == pack.token_estimate

    def test_trims_events_when_over_limit(self) -> None:
        builder = CheckpointBuilder("c2", max_token_estimate=50)
        events = [{"data": "word " * 20} for _ in range(5)]
        summary = "short"
        all_text = summary + " " + " ".join(json.dumps(e) for e in events)
        token_est = CheckpointBuilder.estimate_tokens(all_text)

        pack = CheckpointPack(
            conversation_id="c2",
            summary=summary,
            key_decisions=[],
            recent_events=events,
            token_estimate=token_est,
            created_at=datetime.now(UTC).isoformat(),
        )
        result = builder.compact(pack)
        # Should have fewer events
        assert len(result.recent_events) < len(events)
        assert result.token_estimate <= 50

    def test_trims_summary_when_events_alone_not_enough(self) -> None:
        builder = CheckpointBuilder("c3", max_token_estimate=20)
        long_summary = "word " * 100  # very long summary
        pack = CheckpointPack(
            conversation_id="c3",
            summary=long_summary,
            key_decisions=[],
            recent_events=[],
            token_estimate=CheckpointBuilder.estimate_tokens(long_summary),
            created_at=datetime.now(UTC).isoformat(),
        )
        result = builder.compact(pack)
        assert result.token_estimate <= 20
        assert len(result.summary) < len(long_summary)

"""Tests for steering note injection (ORCH-005)."""

from __future__ import annotations

from agent_orchestrator.orchestrator.steering import SteeringManager, SteeringNote


class TestSteeringNote:
    """SteeringNote dataclass basics."""

    def test_defaults(self) -> None:
        note = SteeringNote(
            conversation_id="conv-1",
            note_text="focus on tests",
            injected_at="2026-03-07T00:00:00+00:00",
        )
        assert note.applied is False
        assert note.conversation_id == "conv-1"
        assert note.note_text == "focus on tests"


class TestSteeringManagerAddNote:
    """Adding notes via SteeringManager."""

    def test_add_note_returns_steering_note(self) -> None:
        mgr = SteeringManager("conv-1")
        note = mgr.add_note("be concise")
        assert isinstance(note, SteeringNote)
        assert note.conversation_id == "conv-1"
        assert note.note_text == "be concise"
        assert note.applied is False
        assert note.injected_at  # non-empty ISO timestamp

    def test_add_multiple_notes(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("note A")
        mgr.add_note("note B")
        assert len(mgr.pending_notes()) == 2


class TestPendingNotes:
    """Filtering pending (unapplied) notes."""

    def test_pending_returns_only_unapplied(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("first")
        mgr.apply_notes()
        mgr.add_note("second")
        pending = mgr.pending_notes()
        assert len(pending) == 1
        assert pending[0].note_text == "second"

    def test_pending_empty_when_all_applied(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("only one")
        mgr.apply_notes()
        assert mgr.pending_notes() == []


class TestApplyNotes:
    """apply_notes marks pending notes as applied."""

    def test_apply_marks_applied(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("do X")
        mgr.add_note("do Y")
        applied = mgr.apply_notes()
        assert len(applied) == 2
        assert all(n.applied for n in applied)

    def test_apply_returns_empty_when_nothing_pending(self) -> None:
        mgr = SteeringManager("conv-1")
        assert mgr.apply_notes() == []

    def test_apply_is_idempotent(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("once")
        mgr.apply_notes()
        # Second call should return nothing
        assert mgr.apply_notes() == []


class TestBuildPromptPrefix:
    """build_prompt_prefix formatting."""

    def test_with_pending_notes(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("focus on error handling")
        mgr.add_note("keep responses short")
        prefix = mgr.build_prompt_prefix()
        assert prefix.startswith("[Steering]")
        assert "- focus on error handling\n" in prefix
        assert "- keep responses short\n" in prefix

    def test_empty_when_no_pending(self) -> None:
        mgr = SteeringManager("conv-1")
        assert mgr.build_prompt_prefix() == ""

    def test_empty_after_all_applied(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("something")
        mgr.apply_notes()
        assert mgr.build_prompt_prefix() == ""


class TestClear:
    """clear removes all notes."""

    def test_clear_removes_all(self) -> None:
        mgr = SteeringManager("conv-1")
        mgr.add_note("a")
        mgr.add_note("b")
        mgr.apply_notes()
        mgr.add_note("c")
        mgr.clear()
        assert mgr.pending_notes() == []
        # Also no applied notes remain (apply returns empty)
        assert mgr.apply_notes() == []


class TestConversationIsolation:
    """Multiple conversations don't interfere."""

    def test_separate_managers_are_independent(self) -> None:
        mgr_a = SteeringManager("conv-A")
        mgr_b = SteeringManager("conv-B")
        mgr_a.add_note("note for A")
        mgr_b.add_note("note for B")
        mgr_b.add_note("another for B")
        assert len(mgr_a.pending_notes()) == 1
        assert len(mgr_b.pending_notes()) == 2
        assert mgr_a.pending_notes()[0].conversation_id == "conv-A"
        assert mgr_b.pending_notes()[0].conversation_id == "conv-B"

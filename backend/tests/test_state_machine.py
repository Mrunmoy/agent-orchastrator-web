"""Tests for the conversation state machine (ORCH-002)."""

from __future__ import annotations

import pytest

from agent_orchestrator.orchestrator.models import ConversationState
from agent_orchestrator.orchestrator.state_machine import (
    InvalidTransition,
    StateMachine,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

S = ConversationState


@pytest.fixture
def sm() -> StateMachine:
    """A fresh state machine starting in QUEUED."""
    return StateMachine(conversation_id="conv-1", initial_state=S.QUEUED)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


class TestInitialState:
    def test_initial_state_is_set(self, sm: StateMachine) -> None:
        assert sm.current_state is S.QUEUED

    def test_conversation_id_stored(self, sm: StateMachine) -> None:
        assert sm.conversation_id == "conv-1"

    def test_history_empty_initially(self, sm: StateMachine) -> None:
        assert sm.history == []


# ---------------------------------------------------------------------------
# Valid transitions
# ---------------------------------------------------------------------------


class TestValidTransitions:
    """Every edge in the directed graph must succeed."""

    @pytest.mark.parametrize(
        "from_state, to_state",
        [
            (S.QUEUED, S.DEBATE),
            (S.DEBATE, S.EXECUTION_PLANNING),
            (S.DEBATE, S.NEEDS_USER_INPUT),
            (S.DEBATE, S.FAILED),
            (S.EXECUTION_PLANNING, S.AUTONOMOUS_WORK),
            (S.EXECUTION_PLANNING, S.NEEDS_USER_INPUT),
            (S.EXECUTION_PLANNING, S.FAILED),
            (S.AUTONOMOUS_WORK, S.COMPLETED),
            (S.AUTONOMOUS_WORK, S.NEEDS_USER_INPUT),
            (S.AUTONOMOUS_WORK, S.FAILED),
            (S.NEEDS_USER_INPUT, S.DEBATE),
            (S.NEEDS_USER_INPUT, S.EXECUTION_PLANNING),
            (S.NEEDS_USER_INPUT, S.AUTONOMOUS_WORK),
            (S.NEEDS_USER_INPUT, S.FAILED),
            (S.FAILED, S.QUEUED),
        ],
    )
    def test_valid_transition(self, from_state: S, to_state: S) -> None:
        sm = StateMachine(conversation_id="c", initial_state=from_state)
        sm.transition(to_state)
        assert sm.current_state is to_state


# ---------------------------------------------------------------------------
# Invalid transitions
# ---------------------------------------------------------------------------


class TestInvalidTransitions:
    """Transitions not in the graph must raise InvalidTransition."""

    @pytest.mark.parametrize(
        "from_state, to_state",
        [
            (S.QUEUED, S.COMPLETED),
            (S.QUEUED, S.AUTONOMOUS_WORK),
            (S.DEBATE, S.COMPLETED),
            (S.DEBATE, S.QUEUED),
            (S.EXECUTION_PLANNING, S.COMPLETED),
            (S.EXECUTION_PLANNING, S.QUEUED),
            (S.AUTONOMOUS_WORK, S.QUEUED),
            (S.AUTONOMOUS_WORK, S.DEBATE),
            (S.FAILED, S.DEBATE),
            (S.FAILED, S.COMPLETED),
        ],
    )
    def test_invalid_transition_raises(self, from_state: S, to_state: S) -> None:
        sm = StateMachine(conversation_id="c", initial_state=from_state)
        with pytest.raises(InvalidTransition):
            sm.transition(to_state)

    def test_self_transition_is_invalid(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.DEBATE)
        with pytest.raises(InvalidTransition):
            sm.transition(S.DEBATE)


# ---------------------------------------------------------------------------
# Terminal state (COMPLETED)
# ---------------------------------------------------------------------------


class TestTerminalState:
    def test_completed_has_no_outgoing(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.COMPLETED)
        for state in S:
            assert not sm.can_transition(state)

    def test_completed_transition_raises(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.COMPLETED)
        with pytest.raises(InvalidTransition):
            sm.transition(S.QUEUED)


# ---------------------------------------------------------------------------
# FAILED -> QUEUED retry
# ---------------------------------------------------------------------------


class TestRetry:
    def test_failed_to_queued(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.FAILED)
        sm.transition(S.QUEUED)
        assert sm.current_state is S.QUEUED


# ---------------------------------------------------------------------------
# Transition history
# ---------------------------------------------------------------------------


class TestHistory:
    def test_history_recorded(self, sm: StateMachine) -> None:
        sm.transition(S.DEBATE)
        assert len(sm.history) == 1
        entry = sm.history[0]
        assert entry[0] is S.QUEUED
        assert entry[1] is S.DEBATE
        # timestamp is a string (ISO-ish)
        assert isinstance(entry[2], str)

    def test_multiple_transitions_recorded(self, sm: StateMachine) -> None:
        sm.transition(S.DEBATE)
        sm.transition(S.EXECUTION_PLANNING)
        sm.transition(S.AUTONOMOUS_WORK)
        assert len(sm.history) == 3
        assert sm.history[0][0] is S.QUEUED
        assert sm.history[2][1] is S.AUTONOMOUS_WORK

    def test_failed_transition_not_recorded(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.QUEUED)
        with pytest.raises(InvalidTransition):
            sm.transition(S.COMPLETED)
        assert sm.history == []


# ---------------------------------------------------------------------------
# can_transition
# ---------------------------------------------------------------------------


class TestCanTransition:
    def test_can_transition_true(self, sm: StateMachine) -> None:
        assert sm.can_transition(S.DEBATE) is True

    def test_can_transition_false(self, sm: StateMachine) -> None:
        assert sm.can_transition(S.COMPLETED) is False

    def test_can_transition_all_from_needs_user_input(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.NEEDS_USER_INPUT)
        assert sm.can_transition(S.DEBATE) is True
        assert sm.can_transition(S.EXECUTION_PLANNING) is True
        assert sm.can_transition(S.AUTONOMOUS_WORK) is True
        assert sm.can_transition(S.FAILED) is True
        assert sm.can_transition(S.COMPLETED) is False
        assert sm.can_transition(S.QUEUED) is False


# ---------------------------------------------------------------------------
# InvalidTransition message content
# ---------------------------------------------------------------------------


class TestInvalidTransitionMessage:
    def test_message_contains_states(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.QUEUED)
        with pytest.raises(InvalidTransition, match="queued"):
            sm.transition(S.COMPLETED)

    def test_message_contains_target_state(self) -> None:
        sm = StateMachine(conversation_id="c", initial_state=S.QUEUED)
        with pytest.raises(InvalidTransition, match="completed"):
            sm.transition(S.COMPLETED)

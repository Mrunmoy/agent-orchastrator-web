"""Conversation state machine (ORCH-002).

Defines valid transitions between ConversationState values and provides
a StateMachine class for tracking conversation lifecycle.
"""

from __future__ import annotations

from datetime import UTC, datetime

from agent_orchestrator.orchestrator.models import ConversationState

# ---------------------------------------------------------------------------
# Transition graph
# ---------------------------------------------------------------------------

S = ConversationState

TRANSITIONS: dict[ConversationState, frozenset[ConversationState]] = {
    S.QUEUED: frozenset({S.DEBATE}),
    S.DEBATE: frozenset({S.EXECUTION_PLANNING, S.NEEDS_USER_INPUT, S.FAILED}),
    S.EXECUTION_PLANNING: frozenset({S.AUTONOMOUS_WORK, S.NEEDS_USER_INPUT, S.FAILED}),
    S.AUTONOMOUS_WORK: frozenset({S.COMPLETED, S.NEEDS_USER_INPUT, S.FAILED}),
    S.NEEDS_USER_INPUT: frozenset(
        {S.DEBATE, S.EXECUTION_PLANNING, S.AUTONOMOUS_WORK, S.FAILED}
    ),
    S.COMPLETED: frozenset(),
    S.FAILED: frozenset({S.QUEUED}),
}


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class InvalidTransition(Exception):  # noqa: N818
    """Raised when a state transition is not allowed."""

    def __init__(self, from_state: ConversationState, to_state: ConversationState) -> None:
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid transition from {from_state.value!r} to {to_state.value!r}"
        )


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


class StateMachine:
    """Tracks conversation state and enforces valid transitions."""

    def __init__(
        self,
        conversation_id: str,
        initial_state: ConversationState,
    ) -> None:
        self._conversation_id = conversation_id
        self._current_state = initial_state
        self._history: list[tuple[ConversationState, ConversationState, str]] = []

    # -- Properties ----------------------------------------------------------

    @property
    def conversation_id(self) -> str:
        return self._conversation_id

    @property
    def current_state(self) -> ConversationState:
        return self._current_state

    @property
    def history(self) -> list[tuple[ConversationState, ConversationState, str]]:
        return list(self._history)

    # -- Public API ----------------------------------------------------------

    def can_transition(self, target_state: ConversationState) -> bool:
        """Return True if *target_state* is reachable from the current state."""
        return target_state in TRANSITIONS.get(self._current_state, frozenset())

    def transition(self, target_state: ConversationState) -> None:
        """Move to *target_state*, or raise InvalidTransition."""
        if not self.can_transition(target_state):
            raise InvalidTransition(self._current_state, target_state)
        prev = self._current_state
        self._current_state = target_state
        self._history.append(
            (prev, target_state, datetime.now(UTC).isoformat())
        )

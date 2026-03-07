# ADR-005: Conversation State Machine Transitions

## Status: Accepted

## Context

Conversations in the orchestrator follow a phased workflow (debate, planning, execution) with user intervention points. We need to enforce valid state transitions so that conversations cannot jump to invalid states (e.g., going from COMPLETED back to DEBATE without going through FAILED first).

## Decision

We implemented an explicit state transition graph with a `StateMachine` class (`backend/src/agent_orchestrator/orchestrator/state_machine.py`).

### State Graph

The seven conversation states and their valid transitions are:

```
QUEUED -----------> DEBATE
DEBATE -----------> EXECUTION_PLANNING | NEEDS_USER_INPUT | FAILED
EXECUTION_PLANNING -> AUTONOMOUS_WORK | NEEDS_USER_INPUT | FAILED
AUTONOMOUS_WORK ---> COMPLETED | NEEDS_USER_INPUT | FAILED
NEEDS_USER_INPUT --> DEBATE | EXECUTION_PLANNING | AUTONOMOUS_WORK | FAILED
COMPLETED ---------> (terminal, no outgoing transitions)
FAILED ------------> QUEUED
```

### Why these states exist

- **QUEUED**: Entry point. A conversation has been created but not yet started. Also the re-entry point after FAILED, allowing retries.
- **DEBATE**: Multi-agent discussion phase where agents argue approaches. This is where design decisions are shaped before any code is written.
- **EXECUTION_PLANNING**: Agents have reached enough agreement to plan concrete work (TDD, task splitting). Transitions from DEBATE.
- **AUTONOMOUS_WORK**: Agents are actively executing code, tests, or documentation. The productive work phase.
- **NEEDS_USER_INPUT**: Any active phase can pause for user guidance. Critically, from NEEDS_USER_INPUT the user can direct the conversation back to any active phase (DEBATE, EXECUTION_PLANNING, or AUTONOMOUS_WORK), enabling course correction.
- **COMPLETED**: Terminal success state. No outgoing transitions -- a completed conversation is immutable.
- **FAILED**: Terminal failure state with one escape: transition back to QUEUED for retry. This allows recovery without creating a new conversation.

### Enforcement mechanism

- `TRANSITIONS` is a `dict[ConversationState, frozenset[ConversationState]]` mapping each state to its valid targets.
- `StateMachine.can_transition(target)` checks membership in the frozenset.
- `StateMachine.transition(target)` raises `InvalidTransition` if the transition is not in the graph. On success, it records the transition (previous state, new state, ISO-8601 timestamp) in `_history`.
- `InvalidTransition` carries both `from_state` and `to_state` for diagnostics.

## Consequences

- **Safety**: Invalid transitions are caught immediately with a clear error message. This prevents bugs where a batch runner or API handler accidentally puts a conversation into an inconsistent state.
- **Auditability**: The `_history` list provides a full trace of all state transitions with timestamps, useful for debugging and for the project saga log.
- **Flexibility at NEEDS_USER_INPUT**: The user can redirect the conversation to any active phase, not just resume where it left off. This is deliberate -- if the debate was going in the wrong direction, the user can send the conversation back to DEBATE from AUTONOMOUS_WORK via NEEDS_USER_INPUT.
- **No automatic transitions**: The state machine only enforces constraints; it does not automatically advance states. The batch runner, API handlers, or other orchestration logic must explicitly call `transition()`.
- **Single retry path**: FAILED can only go to QUEUED, not directly back to DEBATE or any other active state. This forces a clean restart through the normal entry flow.

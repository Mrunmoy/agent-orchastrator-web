# Playbook 04: State Machine Invalid Transition

A conversation has entered an unexpected state, or a state transition is being rejected.

## Symptoms

- `InvalidTransition` exception raised with message: `"Invalid transition from '<current>' to '<target>'"`.
- The exception object carries `from_state` and `to_state` attributes for programmatic inspection.
- A conversation appears stuck because the code is trying to move it to a state that is not reachable from the current state.

## Diagnosis

### 1. Review the transition graph

The valid transitions are defined in `TRANSITIONS` as a dict mapping each `ConversationState` to its allowed target states:

```
QUEUED          -> DEBATE
DEBATE          -> EXECUTION_PLANNING, NEEDS_USER_INPUT, FAILED
EXECUTION_PLANNING -> AUTONOMOUS_WORK, NEEDS_USER_INPUT, FAILED
AUTONOMOUS_WORK -> COMPLETED, NEEDS_USER_INPUT, FAILED
NEEDS_USER_INPUT -> DEBATE, EXECUTION_PLANNING, AUTONOMOUS_WORK, FAILED
COMPLETED       -> (terminal -- no outgoing transitions)
FAILED          -> QUEUED (retry path)
```

### 2. Check the current state

```python
sm = StateMachine(conversation_id="...", initial_state=ConversationState.QUEUED)
print(sm.current_state)  # What state is the conversation actually in?
```

### 3. Check transition history

The `StateMachine.history` property returns a list of `(from_state, to_state, timestamp)` tuples showing every transition that occurred. This is essential for understanding how the conversation reached its current state.

```python
for from_s, to_s, ts in sm.history:
    print(f"{ts}: {from_s.value} -> {to_s.value}")
```

### 4. Use can_transition() to probe

Before attempting a transition, check if it is valid:

```python
if sm.can_transition(ConversationState.AUTONOMOUS_WORK):
    sm.transition(ConversationState.AUTONOMOUS_WORK)
else:
    # Handle: find a valid intermediate state
    pass
```

## Common Invalid Transition Scenarios

### Trying to skip phases

**Example:** Moving from `QUEUED` directly to `AUTONOMOUS_WORK`.
**Fix:** Follow the required path: `QUEUED -> DEBATE -> EXECUTION_PLANNING -> AUTONOMOUS_WORK`.

### Trying to restart a completed conversation

**Example:** Moving from `COMPLETED` to `DEBATE`.
**Fix:** `COMPLETED` is a terminal state with no outgoing transitions. Create a new conversation instead.

### Trying to recover from failure incorrectly

**Example:** Moving from `FAILED` to `DEBATE`.
**Fix:** `FAILED` can only transition to `QUEUED`. Go through `QUEUED -> DEBATE`.

### Returning from user input to the wrong phase

**Example:** Moving from `NEEDS_USER_INPUT` to `COMPLETED`.
**Fix:** `NEEDS_USER_INPUT` can go to `DEBATE`, `EXECUTION_PLANNING`, `AUTONOMOUS_WORK`, or `FAILED` -- but not directly to `COMPLETED`. Route through `AUTONOMOUS_WORK -> COMPLETED`.

## Recovery

### Fix 1: Route through valid intermediate states

If you need to reach a state that is not directly reachable, chain transitions through valid intermediates:

```python
# To go from FAILED to DEBATE:
sm.transition(ConversationState.QUEUED)    # FAILED -> QUEUED
sm.transition(ConversationState.DEBATE)    # QUEUED -> DEBATE
```

### Fix 2: Create a new StateMachine

If the conversation state is truly unrecoverable (e.g., stuck in `COMPLETED` but work is needed), create a new `StateMachine` with the desired initial state for a new conversation:

```python
new_sm = StateMachine(
    conversation_id="new-conversation-id",
    initial_state=ConversationState.QUEUED,
)
```

### Fix 3: Fail and retry

Any state except `COMPLETED` can transition to `FAILED`, and `FAILED` can transition to `QUEUED`. This is the canonical retry path:

```python
sm.transition(ConversationState.FAILED)  # from any non-terminal state
sm.transition(ConversationState.QUEUED)  # reset to start
sm.transition(ConversationState.DEBATE)  # begin again
```

## Code References

- `backend/src/agent_orchestrator/orchestrator/state_machine.py` -- `StateMachine` class, `TRANSITIONS` dict, `InvalidTransition` exception.
- `backend/src/agent_orchestrator/orchestrator/models.py` -- `ConversationState` enum values.

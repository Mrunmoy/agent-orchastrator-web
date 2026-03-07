# Playbook 03: Capacity Overload

The system is resource-constrained and rejecting new agent runs.

## Symptoms

- `ThrottleDecision.allowed` is `False` when calling `CapacityThrottle.check()`.
- `ThrottleDecision.reason` contains a message about exceeding concurrent run limits, CPU, or memory thresholds.
- New conversations are being enqueued in `RunQueue` instead of starting immediately.
- The queue (`RunQueue.pending()`) is growing.

## Diagnosis

### 1. Check the ThrottleDecision reason

The `CapacityThrottle.check()` method returns a `ThrottleDecision` with a human-readable `reason` explaining the denial. There are three possible rejection causes:

**Concurrent run limit exceeded:**
```
"Active concurrent runs (3) >= max (3)"
```

**CPU threshold exceeded:**
```
"CPU usage (87.5%) >= threshold (85.0%)"
```

**Memory threshold exceeded:**
```
"Memory usage (92.3%) >= threshold (90.0%)"
```

### 2. Check active runs

Call `throttle.active_runs()` to see which conversation IDs are currently tracked as active. The throttle uses an `OrderedDict` for deterministic iteration order.

### 3. Review the ThrottlePolicy thresholds

The default `ThrottlePolicy` values are:

| Threshold | Default | Description |
|-----------|---------|-------------|
| `max_concurrent_runs` | 3 | Maximum simultaneous batch runs |
| `max_cpu_percent` | 85.0 | CPU usage ceiling |
| `max_memory_percent` | 90.0 | Memory usage ceiling |

These are set at construction time via `ThrottlePolicy` and are frozen (immutable).

### 4. Check the RunQueue

The `RunQueue` is a FIFO queue for conversations waiting on capacity:

- `queue.pending()` -- list of waiting conversation IDs in order.
- `queue.position(conversation_id)` -- 0-indexed position of a specific conversation, or `None` if not queued.

## Recovery

### Fix 1: Wait for active runs to complete

The simplest fix. When a batch run finishes, call `throttle.release_run(conversation_id)` to free the slot. Then `queue.dequeue()` to get the next waiting conversation.

### Fix 2: Stop lower-priority runs

If a high-priority conversation is blocked, stop a lower-priority active run:

1. Identify active runs: `throttle.active_runs()`.
2. Call `batch_runner.stop()` on the lower-priority run.
3. After it completes, call `throttle.release_run(conversation_id)`.
4. The capacity slot is now free for the high-priority run.

### Fix 3: Adjust ThrottlePolicy thresholds

Create a new `CapacityThrottle` with relaxed limits:

```python
from agent_orchestrator.orchestrator.throttle import ThrottlePolicy, CapacityThrottle

relaxed_policy = ThrottlePolicy(
    max_concurrent_runs=5,    # was 3
    max_cpu_percent=95.0,     # was 85.0
    max_memory_percent=95.0,  # was 90.0
)
throttle = CapacityThrottle(policy=relaxed_policy)
```

**Warning:** Raising thresholds too high risks system instability. CLI agents (especially local Ollama models) consume significant CPU and memory.

### Fix 4: Remove stale active runs

If a batch runner crashed without calling `release_run()`, the throttle will still count it as active. Manually release it:

```python
throttle.release_run("stale-conversation-id")
```

### Fix 5: Drain the queue

To cancel all queued runs:

```python
while True:
    cid = queue.dequeue()
    if cid is None:
        break
    # Handle or discard each conversation
```

Or remove a specific conversation: `queue.remove(conversation_id)`.

## Code References

- `backend/src/agent_orchestrator/orchestrator/throttle.py` -- `CapacityThrottle`, `ThrottlePolicy`, `ThrottleDecision`, `RunQueue`.
- `backend/src/agent_orchestrator/orchestrator/models.py` -- `RunStatus.WAITING_RESOURCES`.
- `backend/src/agent_orchestrator/orchestrator/batch_runner.py` -- how `WAITING_RESOURCES` is set when no agents are available.

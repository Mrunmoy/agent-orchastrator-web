# Playbook 01: Batch Runner Stuck

A batch run hangs or stops progressing through its turns.

## Symptoms

- `BatchRunner.turns_completed` is not advancing.
- `BatchRunner.status` remains `RunStatus.RUNNING` indefinitely.
- The batch completed fewer turns than `batch_size` (default 20) and status is `RunStatus.WAITING_RESOURCES`.
- No new `TurnRecord` entries appearing in the `turn_log`.

## Diagnosis

### 1. Check if the scheduler has no available agents

The `BatchRunner.run()` loop calls `self._scheduler.next_agent()` at the start of each turn. If every agent in the roster has a status other than `AgentStatus.IDLE` (e.g., `RUNNING`, `BLOCKED`, or `OFFLINE`), `next_agent()` returns `None` and the batch transitions to `RunStatus.WAITING_RESOURCES`.

```python
# batch_runner.py lines 101-104
agent = self._scheduler.next_agent()
if agent is None:
    self._status = RunStatus.WAITING_RESOURCES
    break
```

**Check:** Inspect `scheduler.available_agents` -- if the list is empty, all agents are unavailable.

### 2. Check the turn log for adapter errors

Each turn produces a `TurnRecord` with a `status` field from `AdapterStatus`. Look for:

- `AdapterStatus.ERROR` -- the adapter raised an exception during `send_prompt()`.
- `AdapterStatus.TIMED_OUT` -- the CLI agent exceeded its `timeout_seconds` (default 120s).

```python
# batch_runner.py lines 130-138 -- exception handler
except Exception:
    record = TurnRecord(
        ...
        status=AdapterStatus.ERROR,
        ...
    )
```

If every turn is producing `ERROR` status, the adapter or CLI tool is fundamentally broken.

### 3. Check for stuck pause/stop flags

The batch checks `_pause_requested` and `_stop_requested` between turns (lines 147-152). If `pause()` was called, the batch will stop after the current turn with `RunStatus.PAUSED`. If `stop()` was called, it stops with `RunStatus.DONE`. These are not "stuck" states but may appear so if the caller forgot a pause was requested.

## Recovery

### Scenario A: No agents available (WAITING_RESOURCES)

1. Check each agent's status: `scheduler._roster` contains `Agent` objects with a `status` field.
2. If agents are stuck in `RUNNING`, they may have had their turn complete but `mark_agent_status` was not called. The `finally` block in `run()` should reset agents to `IDLE`, but verify.
3. If agents are `OFFLINE`, check that the underlying CLI tool is installed and reachable (see Playbook 02).
4. Fix agent statuses: `scheduler.mark_agent_status(agent_id, AgentStatus.IDLE)`.

### Scenario B: Adapter errors on every turn

1. Follow Playbook 02 to diagnose the adapter.
2. Once the adapter issue is resolved, create a new `BatchRunner` with a fresh scheduler and adapter map.

### Scenario C: Resuming after pause

1. If the batch is `PAUSED`, create a new `BatchRunner` for the remaining turns.
2. Carry forward the conversation context (use the checkpoint system, see Playbook 07).

## Code References

- `backend/src/agent_orchestrator/orchestrator/batch_runner.py` -- `BatchRunner` class, `run()` method, `TurnRecord` and `BatchResult` dataclasses.
- `backend/src/agent_orchestrator/orchestrator/scheduler.py` -- `RoundRobinScheduler.next_agent()`, `available_agents` property.
- `backend/src/agent_orchestrator/orchestrator/models.py` -- `RunStatus` enum (`QUEUED`, `RUNNING`, `PAUSED`, `WAITING_RESOURCES`, `DONE`, `FAILED`), `AgentStatus` enum.

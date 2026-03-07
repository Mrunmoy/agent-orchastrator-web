# Debugging and Recovery Playbooks

Operational playbooks for diagnosing and recovering from common failure modes in the agent orchestrator.

Each playbook follows the structure: **Symptoms** (what you observe), **Diagnosis** (how to confirm the root cause), **Recovery** (step-by-step fix), and **Code References** (relevant source files).

## Playbook Index

| # | Playbook | When to use |
|---|----------|-------------|
| 01 | [Batch Runner Stuck](01-batch-runner-stuck.md) | A batch run hangs or stops progressing |
| 02 | [Adapter Failures](02-adapter-failures.md) | CLI adapters fail consistently with ERROR or TIMED_OUT |
| 03 | [Capacity Overload](03-capacity-overload.md) | System is resource-constrained, new runs rejected |
| 04 | [State Machine Invalid Transition](04-state-machine-invalid-transition.md) | Conversation enters an invalid state |
| 05 | [Merge Conflicts](05-merge-conflicts.md) | Branch merges fail in the merge queue |
| 06 | [Lock Contention](06-lock-contention.md) | Agents block each other on shared resources |
| 07 | [Checkpoint Recovery](07-checkpoint-recovery.md) | Conversation context lost, corrupted, or too large |

## General Debugging Tips

- All orchestrator components are pure logic with no DB writes -- you can inspect state in-memory via the API or by attaching a debugger.
- The `BatchRunner` holds a `_turn_log` list of `TurnRecord` objects -- always check this first for adapter errors.
- Use `StateMachine.history` to trace every state transition with timestamps.
- The `CapacityThrottle` returns a `ThrottleDecision` with a human-readable `reason` string explaining why a run was rejected.
- The `MergeCoordinator.history()` method returns all merge requests regardless of status, useful for post-mortem analysis.

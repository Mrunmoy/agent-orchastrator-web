# ADR-007: Merge Serialization and Lock Policy

## Status: Accepted

## Context

Multiple agents work on separate task branches simultaneously. When their work is ready, branches must be integrated into `main`. Parallel merges risk git conflicts, broken builds, and inconsistent state. We need a coordination mechanism that ensures safe, ordered integration.

## Decision

We implemented single-active-merge semantics via a `MergeCoordinator` FIFO queue (`backend/src/agent_orchestrator/orchestrator/merge_queue.py`) and plan a complementary lock policy (`COORD-002`, not yet implemented).

### MergeCoordinator

The `MergeCoordinator` enforces that only one merge is in progress at any time:

- **Submit**: `submit(task_id, branch_name)` creates a `MergeRequest` with status `PENDING` and adds it to the queue. Duplicate `task_id` submissions raise `ValueError`.
- **Next**: `next()` returns the active `IN_PROGRESS` request if one exists (enforcing single-merge-at-a-time). Otherwise, it advances the first `PENDING` request to `IN_PROGRESS` with a `started_at` timestamp.
- **Complete/Fail/Cancel**: Terminal operations on a merge request:
  - `complete(task_id)` sets status to `MERGED` with a `completed_at` timestamp.
  - `fail(task_id, error)` sets status to `FAILED` with an error message.
  - `cancel(task_id)` sets status to `CANCELLED`.
- **Position tracking**: `position(task_id)` returns the 0-indexed position among `PENDING` items, useful for queue status UI.
- **History**: `history()` returns all requests regardless of status for audit trails.

### MergeRequest lifecycle

```
PENDING --> IN_PROGRESS --> MERGED
                       \-> FAILED
                       \-> CANCELLED
```

### MergeStatus enum

Five states: `PENDING`, `IN_PROGRESS`, `MERGED`, `FAILED`, `CANCELLED`. The enum extends `str` for JSON serialization.

### Lock policy (planned, COORD-002)

The lock policy is designed to complement the merge queue by preventing conflicts earlier in the workflow:

- **Branch locks**: Each task branch is exclusively owned by one agent. No two agents can push to the same branch.
- **File locks**: Critical shared files (e.g., `TASKS.md`, `task-board.md`, `tasks.json`) can be locked by the merge coordinator during integration.
- **Task locks**: A task can only be actively worked on by one agent at a time, enforced at the scheduler level.

These locks are advisory and enforced by the orchestrator, not by git itself.

## Consequences

- **Conflict prevention**: By serializing merges, we eliminate the class of bugs where two branches are merged simultaneously and produce conflicting changes on `main`.
- **Predictable integration order**: FIFO ordering means branches are merged in the order they were submitted, which aligns with the "first to finish, first to merge" principle.
- **Blocking behavior**: If a merge fails, subsequent merges wait. This is intentional -- a failed merge should be investigated before proceeding, since later merges may depend on the failed branch's changes.
- **No automatic retry**: Failed merges stay in `FAILED` status. The operator must investigate, fix, and resubmit. Automatic retry could mask real conflicts.
- **In-memory state**: The coordinator stores all state in memory. If the orchestrator restarts, the merge queue is lost. Persistence (via SQLite) is a future enhancement.
- **Duplicate protection**: The `task_id` uniqueness constraint prevents the same task from being submitted twice, avoiding accidental double-merges.

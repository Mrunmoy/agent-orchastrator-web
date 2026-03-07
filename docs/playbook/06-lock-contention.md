# Playbook 06: Lock Contention

Agents block each other when trying to acquire locks on shared resources.

## Symptoms

- `LockConflictError` raised when an agent tries to acquire a resource lock.
- An agent's status is `AgentStatus.BLOCKED` and cannot proceed with its task.
- The batch runner produces `WAITING_RESOURCES` status because the blocked agent is not `IDLE`.
- Multiple agents are assigned tasks that touch the same files or directories.

## Diagnosis

> **Note:** The lock manager (`COORD-002`) is a planned component. This playbook describes the intended design based on the task specification and domain model. When implemented, the `LockManager` will live at `backend/src/agent_orchestrator/orchestrator/locks.py`.

### 1. Identify the conflicting resource

Lock conflicts occur when two agents (identified by `agent_id`) attempt to acquire a lock on the same resource path. Check:

- Which agent holds the lock (the `owner` field).
- Which agent is requesting it.
- What resource path is contested (e.g., a file path or directory).

### 2. Check agent statuses in the scheduler

```python
for agent in scheduler._roster:
    print(f"{agent.id}: {agent.status.value}")
```

Agents with `AgentStatus.BLOCKED` are waiting for a lock they could not acquire.

### 3. Review task scope assignments

The task board (`docs/coordination/task-board.md`) assigns a `Scope` to each task, defining which files/directories that task may modify. Conflicts arise when scopes overlap.

### 4. Check for expired or stale locks

If an agent crashed or its batch run was stopped without releasing locks, stale locks may remain. The lock manager should provide a `cleanup_expired()` method to release locks that have exceeded their TTL.

## Recovery

### Fix 1: Release stale locks

If a lock is held by an agent that is no longer running:

```python
# When implemented:
lock_manager.release(resource_path, owner=stale_agent_id)
# Or clean up all expired locks:
lock_manager.cleanup_expired()
```

### Fix 2: Reassign tasks to avoid overlap

Review the task board and ensure that concurrently active tasks have non-overlapping scopes:

| Task | Scope | Agent |
|------|-------|-------|
| SETUP-001 | `backend/*` | claude-backend |
| SETUP-002 | `frontend/*` | claude-frontend |

If two tasks must touch the same files, serialize them -- complete one before starting the other.

### Fix 3: Unblock the agent

After releasing the conflicting lock, reset the agent's status so the scheduler can include it in the rotation:

```python
scheduler.mark_agent_status(agent_id, AgentStatus.IDLE)
```

### Fix 4: Coordinate through the merge queue

Instead of having two agents edit the same file simultaneously, use the merge coordinator to serialize their branches:

1. Agent A completes its task and submits to the merge queue.
2. After Agent A's branch is merged, Agent B rebases and continues.

## Prevention

- Design task scopes to be disjoint (different files/directories per task).
- Use the worktree-based development model (`make task-worktree`) to isolate each task's file changes.
- Configure lock TTLs to auto-expire and prevent indefinite blocking.
- Assign one active task per worker agent (enforced by the task board rules).

## Code References

- `backend/src/agent_orchestrator/orchestrator/models.py` -- `AgentStatus` enum (`IDLE`, `RUNNING`, `BLOCKED`, `OFFLINE`).
- `backend/src/agent_orchestrator/orchestrator/scheduler.py` -- `RoundRobinScheduler` skips non-IDLE agents, `mark_agent_status()`.
- `backend/src/agent_orchestrator/orchestrator/merge_queue.py` -- `MergeCoordinator` for serializing branch integration.
- `docs/coordination/task-board.md` -- task scope assignments.
- `config/tasks.json` -- machine-readable task registry with scope fields.

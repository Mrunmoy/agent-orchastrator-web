# Playbook 05: Merge Conflicts

Branch merges fail in the merge coordinator queue.

## Symptoms

- A `MergeRequest` has `status=MergeStatus.FAILED`.
- The `error_message` field on the failed request contains details about the failure.
- The merge queue is blocked because the `MergeCoordinator` enforces single-merge-at-a-time semantics -- a failed merge prevents subsequent pending merges from starting if not properly resolved.
- `MergeCoordinator.active()` returns a request with `MergeStatus.IN_PROGRESS` that is no longer being processed.

## Diagnosis

### 1. Check the failed merge request

```python
coordinator = MergeCoordinator()
# ... after submitting and processing requests ...
for req in coordinator.history():
    if req.status == MergeStatus.FAILED:
        print(f"Task: {req.task_id}")
        print(f"Branch: {req.branch_name}")
        print(f"Error: {req.error_message}")
        print(f"Failed at: {req.completed_at}")
```

### 2. Check for a stuck active merge

The `MergeCoordinator.next()` method will return the currently active (IN_PROGRESS) request if one exists, rather than advancing to the next pending request. This enforces one-at-a-time semantics:

```python
active = coordinator.active()
if active is not None:
    print(f"Stuck merge: {active.task_id} on branch {active.branch_name}")
    print(f"Started at: {active.started_at}")
```

### 3. Identify conflicting files

The `error_message` on a failed merge typically describes which files conflict. Common conflict sources:

- Two agents editing the same source file from different task branches.
- Schema changes in `backend/storage/schema.sql` from concurrent data tasks.
- Shared configuration files (`config/tasks.json`, `docs/coordination/task-board.md`).

### 4. Check the queue state

```python
# Pending requests waiting behind the failure
for req in coordinator.pending():
    print(f"Waiting: {req.task_id} ({req.branch_name})")

# Full history for post-mortem
for req in coordinator.history():
    print(f"{req.task_id}: {req.status.value}")
```

## Recovery

### Fix 1: Resolve conflicts and complete the merge

1. Check out the conflicting branch locally.
2. Merge or rebase against the target branch.
3. Resolve conflicts in the affected files.
4. Complete the merge and mark it in the coordinator:

```python
coordinator.complete(task_id)  # marks as MERGED, sets completed_at
```

### Fix 2: Fail and resubmit

If the merge cannot be resolved immediately:

1. Mark the current merge as failed (if not already):
   ```python
   coordinator.fail(task_id, "Conflicts in src/foo.py -- needs manual resolution")
   ```
2. After resolving conflicts on the branch, submit a new merge request:
   ```python
   coordinator.submit(task_id + "-v2", branch_name)
   ```

### Fix 3: Cancel and re-branch

If the branch is too diverged to merge cleanly:

1. Cancel the merge request:
   ```python
   coordinator.cancel(task_id)  # marks as CANCELLED, sets completed_at
   ```
2. Create a fresh branch from the current main.
3. Cherry-pick or reapply the changes.
4. Submit a new merge request.

### Fix 4: Unblock the queue

After resolving or cancelling the failed/stuck merge, the queue can advance. Call `coordinator.next()` to start the next pending request:

```python
# After completing/failing/cancelling the stuck merge:
next_req = coordinator.next()
if next_req:
    print(f"Now processing: {next_req.task_id}")
```

## Prevention

- Assign non-overlapping file scopes to concurrent tasks (see task board `Scope` column).
- Use the lock policy (COORD-002, when implemented) to prevent agents from editing the same files simultaneously.
- Keep task branches short-lived -- merge frequently to reduce divergence.

## Code References

- `backend/src/agent_orchestrator/orchestrator/merge_queue.py` -- `MergeCoordinator`, `MergeRequest`, `MergeStatus` enum.
- `docs/coordination/task-board.md` -- task scope assignments and merge queue status.

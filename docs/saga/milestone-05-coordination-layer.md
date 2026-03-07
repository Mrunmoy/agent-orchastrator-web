# Milestone 05: Coordination Layer (Batch 3 Parallel Delivery)

## Summary

The third parallel batch focused on coordination and control: steering note injection for user guidance, capacity-aware throttling, orchestration control API endpoints, the intelligence pane UI, and the merge coordinator queue model. This batch had the most review fixes of any batch, with three separate issues caught and corrected.

## Timeline

| PR | Branch | Task | Merge Commit |
|----|--------|------|-------------|
| #11 | `claude/orch-005-steering-notes` | ORCH-005 | `ce74fe7` |
| #12 | `claude/orch-006-capacity-throttle` | ORCH-006 | `c2f4ead` |
| #13 | `claude/coord-001-merge-queue` | COORD-001 | `37b62ca` |
| #14 | `claude/ui-006-intelligence-pane` | UI-006 | `4470f17` |
| #15 | `claude/api-003-orchestration-controls` | API-003 | `5af2239` |

### Review Fix Commits

| Commit | Fix |
|--------|-----|
| `e08c519` | Dedupe `RunQueue.enqueue` for idempotent re-enqueue |
| `2a1b3c1` | Enforce single-active-merge in `MergeCoordinator.next()` |
| `b83b4e1` | Include `paused` in active-run check, validate `batch_size >= 1` |

## What Was Built

### ORCH-005: Steering Note Injection

- **File:** `backend/orchestrator/steering.py`
- Allows users to inject guidance notes between batch windows
- Notes are timestamped and attached to specific conversations
- Validated against active conversation state (cannot steer a completed conversation)
- 13 tests in `backend/tests/test_steering.py`

### ORCH-006: Capacity-Aware Throttle and Run Queue

- **File:** `backend/orchestrator/throttle.py`
- `RunQueue` for ordering pending conversation runs
- Throttle checks CPU/RAM/active-agent capacity before starting new runs
- Queue/resume policy: conversations are queued when capacity is exceeded, resumed when resources free up
- **Review finding:** `RunQueue.enqueue` did not deduplicate. Calling enqueue twice for the same conversation created a duplicate entry. Fixed in `e08c519` for idempotent behavior.
- **Review finding:** Active-run check did not count `paused` runs as active, allowing over-scheduling. `batch_size` parameter was not validated (could be 0 or negative). Both fixed in `b83b4e1`.
- 23 tests in `backend/tests/test_throttle.py`

### COORD-001: Merge Coordinator Queue Model

- **File:** `backend/orchestrator/merge_queue.py`
- Serialized merge queue: one branch integrates at a time
- Priority ordering, conflict detection, rollback support
- **Review finding:** `MergeCoordinator.next()` could return multiple active merges simultaneously. Fixed in `2a1b3c1` to enforce single-active-merge invariant.
- 20 tests in `backend/tests/test_merge_queue.py`

### UI-006: Intelligence Pane

- **Files:** `frontend/src/features/intelligence/IntelligencePane.tsx`, `AgreementBar.tsx`, `MemoCard.tsx`
- Displays agreement/disagreement metrics between agents
- Renders neutral decision memos from Ollama
- 14 tests across `IntelligencePane.test.tsx` (3), `AgreementBar.test.tsx` (5), `MemoCard.test.tsx` (6)

### API-003: Orchestration Control Endpoints

- **File:** `backend/api/routes/orchestration.py`
- Endpoints: `POST /run`, `POST /continue`, `POST /stop`, `POST /steer`
- Integrates with batch runner, steering, and throttle
- Uses shared `db_provider` pattern established in Batch 1
- 23 tests in `backend/tests/test_api_orchestration.py`

## Tests Added This Batch

| Component | Tests |
|-----------|-------|
| Steering notes | 13 |
| Capacity throttle | 23 |
| Merge coordinator | 20 |
| Intelligence pane (frontend) | 14 |
| Orchestration control API | 23 |
| **Total** | **93** |

## Key Review Themes

This batch surfaced three classes of bugs:

1. **Idempotency** -- the enqueue operation was not safe to retry (`e08c519`)
2. **Invariant enforcement** -- the single-active-merge constraint was not enforced at the model level (`2a1b3c1`)
3. **State completeness** -- the `paused` state was not considered "active" for capacity checks (`b83b4e1`)

All three were caught in PR review and fixed before the next batch started.

## What This Unblocked

- API-003 unblocked UI-004 (composer + run controls) -- the last P0 UI task
- ORCH-005 unblocked UI-007 (run-window controls and steering)
- ORCH-006 unblocked COORD-003 (notification pipeline)
- COORD-001 unblocked COORD-002 (branch/task lock policy)
- With this batch complete, the system was functionally end-to-end: users could create conversations, configure agents, start runs, steer them, and observe results through the intelligence pane

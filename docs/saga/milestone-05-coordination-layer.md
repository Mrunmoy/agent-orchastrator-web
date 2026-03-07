# Quest 05: Third Raid -- The War Room

> *With the execution engine running, the party builds the coordination layer: steering notes for the Dungeon Master to guide agents mid-battle, capacity throttling so the system doesn't burn itself out, the orchestration API to control everything from the outside, an intelligence pane to visualize agent agreement, and a merge coordinator to keep branches from colliding. This raid has the most review fixes of any -- three bugs caught, three bugs squashed.*

## Raid Composition

| PR | Task | Objective | Tests |
|----|------|-----------|-------|
| #11 | ORCH-005 | Steering note injection | 13 |
| #12 | ORCH-006 | Capacity-aware throttle + run queue | 23 |
| #13 | COORD-001 | Merge coordinator queue model | 20 |
| #14 | UI-006 | Intelligence pane | 14 |
| #15 | API-003 | Orchestration control endpoints | 23 |

## Loot Gained

### ORCH-005: Steering Notes
- **Drop:** `backend/orchestrator/steering.py`
- SteeringManager: add notes, mark as applied, build prompt prefix for agent injection
- Conversations are isolated -- notes from one don't leak to another

### ORCH-006: Capacity Throttle
- **Drop:** `backend/orchestrator/throttle.py`
- ThrottlePolicy: max 3 concurrent runs, 85% CPU ceiling, 90% memory ceiling
- ThrottleDecision: allowed/denied with reason
- RunQueue: FIFO queue for conversations waiting on capacity

### COORD-001: Merge Coordinator
- **Drop:** `backend/orchestrator/merge_queue.py`
- MergeRequest lifecycle: PENDING --> IN_PROGRESS --> MERGED/FAILED/CANCELLED
- Single-active-merge semantics (review fix -- see traps)
- FIFO ordering, position tracking, history

### UI-006: Intelligence Pane
- **Drop:** `frontend/src/features/intelligence/`
- AgreementBar: colored segments by agreement level with agent names on hover
- MemoCard: displays neutral memo (summary, key points, recommendation)
- IntelligencePane: container with empty states

### API-003: Orchestration Controls
- **Drop:** `backend/api/routes/orchestration.py`
- POST `/run` -- start a batch (validates batch_size >= 1, blocks if active run exists including paused)
- POST `/continue` -- resume a paused run
- POST `/stop` -- stop any active run
- POST `/steer` -- inject a steering note (validates non-empty)

## Traps and Review Findings

This raid hit three distinct trap categories:

| Trap | Category | What Went Wrong | Fix |
|------|----------|----------------|-----|
| Duplicate enqueue | Idempotency | `RunQueue.enqueue` could queue the same conversation twice, causing duplicate run attempts | Made enqueue idempotent -- returns existing position if already queued |
| Multiple active merges | Invariant violation | `MergeCoordinator.next()` would happily start a second merge while one was already in progress, defeating the whole point | `next()` now returns the active IN_PROGRESS request instead of advancing |
| Paused not counted as active | State completeness | Starting a new run didn't check for paused runs -- you could have two lifecycle records for the same conversation | Added `paused` to the active-run conflict check; also validated `batch_size >= 1` |

All three caught in PR review, fixed and re-pushed before the next raid.

## Loot Summary

93 tests (79 backend + 14 frontend). Heaviest backend haul of any raid.

## Map Unlocked

- API-003 --> UI-004 (composer + run controls) -- the last P0
- ORCH-005 --> UI-007 (run-window controls and steering)
- ORCH-006 --> COORD-003 (notification pipeline)
- COORD-001 --> COORD-002 (branch/task lock policy)

With this raid complete, the system is functionally end-to-end: create conversations, configure agents, start runs, steer them, observe results through the intelligence pane.

*The war room is operational. The Dungeon Master has full control.*

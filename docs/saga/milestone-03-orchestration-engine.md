# Milestone 03: Orchestration Engine (Batch 1 Parallel Delivery)

## Summary

This was the first milestone to use the full PR-based parallel delivery workflow. Five tasks ran simultaneously in isolated git worktrees, each producing a PR that went through CI and review before merging. The conversation state machine, round-robin scheduler, agent config API, events stream, and history pane were all delivered in this batch.

## Timeline

PRs #1 through #5, merged with review fixes applied between merges.

| PR | Branch | Task | Merge Commit |
|----|--------|------|-------------|
| #4 | `claude/orch-002-state-machine` | ORCH-002 | `694a807` |
| #5 | `claude/api-004-agent-config` | API-004 | `06bf607` |
| #1 | `claude/ui-002-history-pane` | UI-002 | `9745a10` |
| #2 | `claude/orch-003-scheduler` | ORCH-003 | `fdfc6de` |
| #3 | `claude/api-005-events-stream` | API-005 | `2e29fc8` |

### Review Fix Commits (landed between PR merges)

| Commit | Fix |
|--------|-----|
| `9dce5ae` | Add missing `queued` and `execution_planning` states to state machine |
| `ed61192` | Restrict scheduler to IDLE-only agents |
| `35d22ed` | Validate `n > 0` in `/events/latest` endpoint |
| `6130453` | Share single `db_provider` across all routes (was creating separate instances) |

### Merge Conflict Resolutions

- `f669a04` -- Resolve merge conflict with main in ORCH-003 branch
- `e3e567e` -- Resolve merge conflict with main in API-005 branch

## What Was Built

### ORCH-002: Conversation State Machine

- **File:** `backend/orchestrator/state_machine.py`
- States: `Idle`, `Queued`, `ExecutionPlanning`, `Debate`, `Planning`, `Working`, `NeedsInput`, `Completed`, `Failed`
- Transition validation: only legal state transitions are allowed
- **Review finding:** Two states (`Queued`, `ExecutionPlanning`) were missing from the initial implementation and added in review fix `9dce5ae`
- 17 tests in `backend/tests/test_state_machine.py`

### ORCH-003: Round-Robin Scheduler

- **File:** `backend/orchestrator/scheduler.py`
- Strict agent ordering with round-robin turn assignment
- **Key decision:** Scheduler only considers agents in `IDLE` status. This was a review fix (`ed61192`) -- the initial implementation would schedule busy agents.
- 12 tests in `backend/tests/test_scheduler.py`

### API-004: Agent Config CRUD

- **File:** `backend/api/routes/agents.py`
- Endpoints for agent name, role, personality, order, working directory
- 12 tests in `backend/tests/test_api_agents.py`

### API-005: Events Stream

- **File:** `backend/api/routes/events.py`
- SSE-style endpoint for UI live updates
- `/events/latest?n=N` for polling with validation
- **Review finding:** `n > 0` validation was missing, added in `35d22ed`
- 10 tests in `backend/tests/test_api_events.py`

### UI-002: Conversation History Pane

- **Files:** `frontend/src/features/history/ConversationList.tsx`, `ConversationItem.tsx`
- Scroll, select, delete, clear all, status icon display
- 19 tests across `ConversationList.test.tsx` (7) and `ConversationItem.test.tsx` (12)

## Key Decision: Shared db_provider

The most significant review finding was commit `6130453`: each route module was creating its own `DatabaseManager` instance, leading to separate connection pools and potential data inconsistency. The fix introduced a single shared `db_provider` injected via FastAPI dependency injection. This pattern was carried forward into all subsequent API routes.

## Tests Added This Batch

| Component | Tests |
|-----------|-------|
| State machine | 17 |
| Scheduler | 12 |
| Agent config API | 12 |
| Events API | 10 |
| History pane (frontend) | 19 |
| **Total** | **70** |

## What This Unblocked

- ORCH-002 + ORCH-003 unblocked ORCH-004 (batch runner)
- API-004 unblocked UI-005 (agent roster editor)
- API-005 unblocked UI-003 (chat timeline) and UI-006 (intelligence pane)
- UI-002 established the pattern for all subsequent feature components

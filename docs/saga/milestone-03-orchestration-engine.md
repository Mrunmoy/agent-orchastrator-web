# Quest 03: First Raid -- The Engine Room

> *The party's first true parallel raid. Five adventurers enter five separate worktree dungeons simultaneously. They emerge with the conversation state machine, the round-robin scheduler, agent config APIs, an events stream, and the conversation history pane. But not without some close calls in review.*

## Raid Composition

Five tasks, five worktrees, five PRs. The first time the full parallel workflow was deployed.

| PR | Task | Objective | Tests |
|----|------|-----------|-------|
| #4 | ORCH-002 | Conversation state machine | 17 |
| #5 | API-004 | Agent config CRUD endpoints | 12 |
| #1 | UI-002 | Conversation history pane | 19 |
| #2 | ORCH-003 | Round-robin scheduler | 12 |
| #3 | API-005 | Events stream endpoint | 10 |

## Loot Gained

### ORCH-002: The State Machine
- **Drop:** `backend/orchestrator/state_machine.py`
- 7 conversation states: Idle, Queued, ExecutionPlanning, Debate, Planning, Working, NeedsInput, Completed, Failed
- Transition validation -- only legal moves allowed, InvalidTransition exception for the rest

### ORCH-003: The Scheduler
- **Drop:** `backend/orchestrator/scheduler.py`
- Round-robin turn assignment with wrap-around
- Only considers IDLE agents (review fix -- see traps below)

### API-004: Agent Config
- **Drop:** `backend/api/routes/agents.py`
- CRUD for agent name, role, personality, order, working directory

### API-005: Events Stream
- **Drop:** `backend/api/routes/events.py`
- SSE-style endpoint for UI live updates, `/events/latest?n=N` for polling

### UI-002: History Pane
- **Drop:** `frontend/src/features/history/`
- ConversationList + ConversationItem with scroll, select, delete, status icons

## Traps and Review Findings

The Dungeon Master caught four issues in review. All fixed before the next raid.

| Trap | What Went Wrong | Fix |
|------|----------------|-----|
| Missing states | State machine was missing `queued` and `execution_planning` | Added in review fix |
| Over-scheduling | Scheduler was assigning turns to RUNNING agents, not just IDLE | Restricted to IDLE-only |
| No validation | `/events/latest?n=0` was accepted (should require n > 0) | Added validation |
| DB isolation | Each route was creating its own DatabaseManager -- separate connections, potential data drift | Created shared `db_provider.py` module |

The **shared db_provider** fix was the most significant. It established the pattern used by every API route going forward: one DB instance, injected via dependency.

## Merge Conflicts Resolved

Two branches collided with main during the raid:
- ORCH-003 branch -- resolved and merged
- API-005 branch -- resolved and merged

## Loot Summary

70 tests (51 backend + 19 frontend).

## Map Unlocked

- ORCH-002 + ORCH-003 --> ORCH-004 (the batch runner -- the big boss)
- API-004 --> UI-005 (agent roster editor)
- API-005 --> UI-003 (chat timeline), UI-006 (intelligence pane)
- The history pane (UI-002) set the component pattern for all future frontend work

*The engine room is online. The party can feel the machinery humming. Next stop: the batch forge.*

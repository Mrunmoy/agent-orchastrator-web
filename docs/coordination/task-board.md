# Task Board

Use this board to assign independent slices to parallel agents.

## Rules
- One owner per task.
- One active task per agent.
- Keep tasks mergeable in <= 1 day.
- Merge coordinator integrates to `master` sequentially.

## Columns
- `Todo`
- `In Progress`
- `Review`
- `Done`
- `Blocked`

## Tasks

| ID | Title | Scope | Owner | Status | Depends On | Notes |
|---|---|---|---|---|---|---|
| UI-001 | Conversation list component | `src/ui/conversations/*` | unassigned | Todo | none | Scroll, delete, clear-all |
| UI-002 | Chat timeline component | `src/ui/chat/*` | unassigned | Todo | none | Avatar, name, timestamp |
| ORCH-001 | Batch runner (20-turn window) | `backend/orchestrator/batch_runner.py` | unassigned | Todo | none | Pause/resume + steering note |
| ORCH-002 | Round-robin scheduler | `backend/orchestrator/scheduler.py` | unassigned | Todo | ORCH-001 | Respect agent order |
| DATA-001 | SQLite schema v1 | `backend/storage/schema.sql` | unassigned | Todo | none | conversations, agents, tasks, checkpoints |
| DATA-002 | Checkpoint compressor | `backend/storage/checkpoint.py` | unassigned | Todo | DATA-001 | token-bounded context packs |
| OPS-001 | Capacity monitor | `backend/runtime/capacity.py` | unassigned | Todo | none | CPU/RAM/agent-availability gating |
| OPS-002 | Notification status model | `backend/runtime/notifications.py` | unassigned | Todo | OPS-001 | Needs Input / Failed / Complete |

## Merge Queue

| Order | Branch | PR/Commit | Status |
|---|---|---|---|
| 1 | - | - | waiting |
| 2 | - | - | waiting |
| 3 | - | - | waiting |


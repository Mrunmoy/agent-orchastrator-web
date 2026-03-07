# Task Board

Execution board for active parallel slices.

## Status Legend
- `Todo`
- `In Progress`
- `Review`
- `Done`
- `Blocked`

## Rules
- No task starts unless owner is assigned.
- One active task per worker agent.
- Worker never merges to `master` directly.
- Merge coordinator integrates one branch at a time.
- This board must mirror `config/tasks.json` IDs.

## Ready Queue (Real Tasks)

| ID | Title | Scope | Priority | Owner | Status | Depends On | Branch |
|---|---|---|---|---|---|---|---|
| SETUP-001 | Backend Python package layout | `backend/*` | P0 | claude-backend | Review | none | claude/setup-backend-layout |
| SETUP-002 | Frontend TypeScript app shell | `frontend/*` | P0 | claude-frontend | Done | none | claude/setup-frontend-shell |
| DATA-001 | SQLite schema v1 | `backend/storage/schema.sql` | P0 | unassigned | Todo | SETUP-001 | - |
| ORCH-001 | Domain models | `backend/orchestrator/models.py` | P0 | unassigned | Todo | SETUP-001,DATA-001 | - |
| ORCH-003 | Round-robin scheduler | `backend/orchestrator/scheduler.py` | P0 | unassigned | Todo | ORCH-001 | - |
| ORCH-004 | 20-turn batch runner | `backend/orchestrator/batch_runner.py` | P0 | unassigned | Todo | ORCH-003,ADPT-001,ADPT-002 | - |
| ADPT-001 | Claude CLI adapter | `backend/adapters/claude_adapter.py` | P0 | unassigned | Todo | SETUP-001 | - |
| ADPT-002 | Codex CLI adapter | `backend/adapters/codex_adapter.py` | P0 | unassigned | Todo | SETUP-001 | - |
| API-001 | FastAPI app + health | `backend/api/app.py` | P0 | unassigned | Todo | SETUP-001 | - |
| API-003 | Run/continue/stop/steer endpoints | `backend/api/routes/orchestration.py` | P0 | unassigned | Todo | API-001,ORCH-004 | - |
| UI-001 | App shell layout | `frontend/src/layout/*` | P0 | unassigned | Todo | SETUP-002 | - |
| UI-002 | Conversation history pane | `frontend/src/features/history/*` | P0 | unassigned | Todo | UI-001,API-002 | - |
| UI-003 | Chat timeline | `frontend/src/features/chat/*` | P0 | unassigned | Todo | UI-001,API-005 | - |
| UI-004 | Composer + run controls | `frontend/src/features/composer/*` | P0 | unassigned | Todo | UI-001,API-003 | - |
| COORD-001 | Merge coordinator queue model | `backend/orchestrator/merge_queue.py` | P1 | unassigned | Todo | ORCH-004 | - |
| OPS-003 | Capacity telemetry snapshot | `backend/runtime/capacity.py` | P1 | unassigned | Todo | SETUP-001 | - |
| TEST-001 | Scheduler and batch unit tests | `backend/tests/orchestrator/*` | P1 | unassigned | Todo | ORCH-003,ORCH-004 | - |
| TEST-003 | Frontend component tests | `frontend/tests/*` | P1 | unassigned | Todo | UI-002,UI-003,UI-004 | - |

## Merge Queue

| Order | Branch | Task ID | Status |
|---|---|---|---|
| 1 | - | - | waiting |
| 2 | - | - | waiting |
| 3 | - | - | waiting |

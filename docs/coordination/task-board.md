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
| SETUP-001 | Backend Python package layout | `backend/*` | P0 | claude-backend | Done | none | claude/setup-backend-layout |
| SETUP-002 | Frontend TypeScript app shell | `frontend/*` | P0 | claude-frontend | Done | none | claude/setup-frontend-shell |
| SETUP-003 | Shared dev commands | `Makefile,scripts/*` | P1 | claude-parallel | Done | SETUP-001,SETUP-002 | master (merged) |
| DATA-001 | SQLite schema v1 | `backend/storage/schema.sql` | P0 | claude-data | Done | SETUP-001 | claude/data-sqlite-schema-v1 |
| DATA-002 | Migration/bootstrap loader | `backend/storage/db.py` | P1 | claude-parallel | Done | DATA-001 | master (merged) |
| DATA-003 | JSONL event log writer/reader | `backend/storage/event_log.py` | P1 | claude-parallel | Done | SETUP-001 | master (merged) |
| DATA-004 | Checkpoint pack builder | `backend/storage/checkpoint.py` | P1 | claude-agent | Done | DATA-001,DATA-003 | claude/data-004-checkpoint-packer |
| ORCH-001 | Domain models | `backend/orchestrator/models.py` | P0 | claude-parallel | Done | SETUP-001,DATA-001 | master (merged) |
| ORCH-002 | Conversation state machine | `backend/orchestrator/state_machine.py` | P0 | claude-agent | Done | ORCH-001 | claude/orch-002-state-machine |
| ORCH-003 | Round-robin scheduler | `backend/orchestrator/scheduler.py` | P0 | claude-agent | Done | ORCH-001 | claude/orch-003-scheduler |
| ORCH-004 | 20-turn batch runner | `backend/orchestrator/batch_runner.py` | P0 | claude-agent | Done | ORCH-002,ORCH-003 | claude/orch-004-batch-runner |
| ORCH-005 | Steering note injection | `backend/orchestrator/steering.py` | P1 | claude-agent | Done | ORCH-004 | claude/orch-005-steering-notes |
| ORCH-006 | Capacity-aware throttle | `backend/orchestrator/throttle.py` | P1 | claude-agent | Done | ORCH-004,OPS-003 | claude/orch-006-capacity-throttle |
| ADPT-001 | Claude CLI adapter | `backend/adapters/claude_adapter.py` | P0 | claude-adapter | Done | SETUP-001 | claude/adpt-claude-cli |
| ADPT-002 | Codex CLI adapter | `backend/adapters/codex_adapter.py` | P0 | codex-adapter | Done | SETUP-001 | codex/adpt-codex-cli |
| ADPT-003 | Ollama memo adapter | `backend/adapters/ollama_adapter.py` | P1 | claude-parallel | Done | SETUP-001 | master (merged) |
| ADPT-004 | Adapter output normalization | `backend/adapters/normalize.py` | P1 | claude-agent | Done | ADPT-001,ADPT-002,ADPT-003 | claude/adpt-004-output-normalization |
| API-001 | FastAPI app + health | `backend/api/` | P0 | claude-parallel | Done | SETUP-001 | master (merged) |
| API-002 | Conversation CRUD endpoints | `backend/api/routes/conversations.py` | P0 | claude-parallel | Done | API-001,DATA-001 | master (merged) |
| API-003 | Orchestration control endpoints | `backend/api/routes/orchestration.py` | P0 | claude-agent | Done | API-001,ORCH-004 | claude/api-003-orchestration-controls |
| API-004 | Agent config endpoints | `backend/api/routes/agents.py` | P1 | claude-agent | Done | API-001,ORCH-001 | claude/api-004-agent-config |
| API-005 | Events stream endpoint | `backend/api/routes/events.py` | P1 | claude-agent | Done | API-001,DATA-003 | claude/api-005-events-stream |
| UI-001 | App shell layout | `frontend/src/layout/*` | P0 | claude-ui | Done | SETUP-002 | claude/ui-app-shell-layout |
| UI-002 | Conversation history pane | `frontend/src/features/history/*` | P0 | claude-agent | Done | UI-001,API-002 | claude/ui-002-history-pane |
| UI-003 | Chat timeline | `frontend/src/features/chat/*` | P0 | claude-agent | Done | UI-001,API-005 | claude/ui-003-chat-timeline |
| UI-004 | Composer + run controls | `frontend/src/features/composer/*` | P0 | claude-agent | Done | UI-001,API-003 | claude/ui-004-composer-controls |
| UI-005 | Agent roster editor | `frontend/src/features/agents/*` | P1 | claude-agent | Done | UI-001,API-004 | claude/ui-005-agent-roster |
| UI-006 | Intelligence pane | `frontend/src/features/intelligence/*` | P1 | claude-agent | Done | UI-001,API-005,ADPT-003 | claude/ui-006-intelligence-pane |
| UI-007 | Run-window controls | `frontend/src/features/run-controls/*` | P1 | claude-agent | Done | UI-004,ORCH-005 | claude/ui-007-run-window-controls |
| UI-008 | New conversation form (title + working directory) | `frontend/src/layout/AppShell.tsx` | P0 | copilot | Done | UI-002,API-002 | copilot/fix-new-conversation-button |
| COORD-001 | Merge coordinator queue model | `backend/orchestrator/merge_queue.py` | P1 | claude-agent | Done | ORCH-004 | claude/coord-001-merge-queue |
| COORD-002 | Task/branch lock policy | `backend/orchestrator/locks.py` | P1 | claude-agent | Done | COORD-001 | claude/coord-002-task-locks |
| COORD-003 | Notification pipeline | `backend/runtime/notifications.py` | P1 | claude-agent | Done | ORCH-006 | claude/coord-003-notifications |
| OPS-001 | Local auth token and request limits | `backend/api/security.py` | P1 | claude-agent | Done | API-001 | claude/ops-001-auth-limits |
| OPS-002 | LAN startup/run profile | `scripts/run_lan.sh` | P2 | claude-agent | Done | API-001,UI-001 | claude/ops-002-lan-startup-profile |
| OPS-003 | Capacity telemetry snapshot | `backend/runtime/capacity.py` | P1 | claude-parallel | Done | SETUP-001 | master (merged) |
| TEST-001 | Orchestrator unit tests | `backend/tests/orchestrator/*` | P1 | claude-agent | Done | ORCH-003,ORCH-004 | (inline with impl) |
| TEST-002 | Adapter contract tests | `backend/tests/adapters/*` | P1 | claude-agent | Done | ADPT-001,ADPT-002 | claude/test-002-adapter-contracts |
| TEST-003 | Frontend component tests | `frontend/tests/*` | P1 | claude-agent | Done | UI-002,UI-003,UI-004 | (inline with impl) |
| TEST-004 | E2E scenario test | `tests/e2e/*` | P2 | claude-agent | Done | API-003,UI-004,COORD-003 | claude/test-004-e2e-happy-path |
| DOC-001 | ADR entries | `docs/decisions/*` | P2 | claude-agent | Done | ORCH-004 | claude/doc-001-adr-entries |
| DOC-002 | Playbook recovery | `docs/playbook/*` | P2 | claude-agent | Done | TEST-001 | claude/doc-002-playbooks |
| DOC-003 | Project saga milestones | `docs/saga/*` | P2 | claude-agent | Done | SETUP-002 | claude/doc-003-saga-log |

## Merge Queue

| Order | Branch | Task ID | Status |
|---|---|---|---|
| 1 | worktree-agent (API-001) | API-001 | merged |
| 2 | worktree-agent (DATA-002) | DATA-002 | merged |
| 3 | worktree-agent (OPS-003) | OPS-003 | merged |
| 4 | worktree-agent (ORCH-001) | ORCH-001 | merged |
| 5 | worktree-agent (ADPT-003) | ADPT-003 | merged |
| 6 | worktree-agent (DATA-003) | DATA-003 | merged |
| 7 | worktree-agent (API-002) | API-002 | merged |
| 8 | PR #1 ORCH-002 | ORCH-002 | merged |
| 9 | PR #2 ORCH-003 | ORCH-003 | merged |
| 10 | PR #3 API-005 | API-005 | merged |
| 11 | PR #4 API-004 | API-004 | merged |
| 12 | PR #5 UI-002 | UI-002 | merged |
| 13 | PR #6 ADPT-004 | ADPT-004 | merged |
| 14 | PR #7 DATA-004 | DATA-004 | merged |
| 15 | PR #8 ORCH-004 | ORCH-004 | merged |
| 16 | PR #9 UI-003 | UI-003 | merged |
| 17 | PR #10 UI-005 | UI-005 | merged |
| 18 | PR #11 ORCH-005 | ORCH-005 | merged |
| 19 | PR #12 ORCH-006 | ORCH-006 | merged |
| 20 | PR #13 COORD-001 | COORD-001 | merged |
| 21 | PR #14 UI-006 | UI-006 | merged |
| 22 | PR #15 API-003 | API-003 | merged |
| 23 | copilot/fix-new-conversation-button (UI-008) | UI-008 | in review |

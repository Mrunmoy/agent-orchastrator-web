# Milestone 02: Core Infrastructure

## Summary

With foundations in place, the core infrastructure milestone built out the data layer (SQLite schema, DatabaseManager, JSONL event log), all three CLI adapters (Claude, Codex, Ollama), the FastAPI application with health and conversation CRUD endpoints, domain models, and capacity telemetry. This was the densest milestone, completing 10 tasks across 5 epics.

## Timeline

Tasks were completed in a mix of direct merges and the early merge-queue workflow. The merge queue (documented in `docs/coordination/task-board.md`) serialized integration of 7 parallel branches.

| Commit | Task | Description |
|--------|------|-------------|
| `de588f4` | ADPT-001 | Add Claude CLI adapter with base interface and tests |
| `a89f1f1` | DATA-001 | Add SQLite schema v1 with tests |
| `f1caebd` | ADPT-002 | Implement Codex CLI adapter |
| `b49e58f` | UI-001 | Implement app shell layout components |
| `ae6a570` | API-001 | Add FastAPI app with health and state endpoints |
| `f5c3124` | DATA-002 | Add DatabaseManager for schema bootstrap and connection management |
| `7f85415` | OPS-003 | Add capacity telemetry snapshot with threshold gates |
| `4b6726f` | ORCH-001 | Add domain models with 9 enums and 8 dataclasses |
| `8d9a944` | ADPT-003 | Add Ollama memo adapter with stdin piping |
| `b166be9` | DATA-003 | Add append-only JSONL event log writer/reader |
| `d109a85` | API-002 | Add conversation CRUD endpoints with soft-delete |

### Merge Queue Order (first serialized integration)

| Order | Task | Status |
|-------|------|--------|
| 1 | API-001 | merged |
| 2 | DATA-002 | merged |
| 3 | OPS-003 | merged |
| 4 | ORCH-001 | merged |
| 5 | ADPT-003 | merged |
| 6 | DATA-003 | merged |
| 7 | API-002 | merged |

## What Was Built

### DATA-001: SQLite Schema v1

- **File:** `backend/storage/schema.sql`
- Tables: `conversations`, `agents`, `tasks`, `runs`, `checkpoints`
- 11 tests in `backend/tests/test_schema.py`
- **Owner:** `claude-data`

### DATA-002: DatabaseManager

- **File:** `backend/storage/db.py`
- Bootstrap loader that applies schema on first connection
- Connection pooling and transaction helpers
- 14 tests in `backend/tests/test_db_manager.py`

### DATA-003: JSONL Event Log

- **File:** `backend/storage/event_log.py`
- Append-only writer with structured event envelope (timestamp, type, payload)
- Reader with filtering and tail support
- 17 tests in `backend/tests/test_event_log.py`

### ADPT-001: Claude CLI Adapter

- **File:** `backend/adapters/claude_adapter.py`
- Base adapter interface (`AdapterBase`) defining the contract for all adapters
- Session attach/resume hooks, timeout handling with configurable limits
- 14 tests in `backend/tests/test_claude_adapter.py`
- **Owner:** `claude-adapter`

### ADPT-002: Codex CLI Adapter

- **File:** `backend/adapters/codex_adapter.py`
- Implements the same `AdapterBase` interface for OpenAI Codex CLI
- 16 tests in `backend/tests/test_codex_adapter.py`
- **Owner:** `codex-adapter`

### ADPT-003: Ollama Memo Adapter

- **File:** `backend/adapters/ollama_adapter.py`
- Neutral decision memo generator using Ollama with stdin piping
- Availability check for local Ollama installation
- 15 tests in `backend/tests/test_ollama_adapter.py`

### API-001: FastAPI App + Health Endpoints

- **File:** `backend/api/app.py`, `backend/api/routes/health.py`
- Health check endpoint, state endpoint, CORS configuration
- 9 tests in `backend/tests/test_api_health.py`

### API-002: Conversation CRUD

- **File:** `backend/api/routes/conversations.py`
- Create, read, update, delete (soft-delete), list, and select endpoints
- Preserves conversation recency on select (commit `39c03c5`)
- 22 tests in `backend/tests/test_api_conversations.py`

### ORCH-001: Domain Models

- **File:** `backend/orchestrator/models.py`
- 9 enums: `AgentSource`, `AgentStatus`, `ConversationState`, `TaskStatus`, `RunPhase`, `NotificationType`, `EventType`, `Priority`, `Role`
- 8 dataclasses: `Agent`, `Conversation`, `Task`, `RunWindow`, `Notification`, `Event`, `Checkpoint`, `SteeringNote`
- 43 tests in `backend/tests/test_orchestrator_models.py`

### OPS-003: Capacity Telemetry

- **File:** `backend/runtime/capacity.py`
- CPU/RAM/active-agent-run snapshot with threshold gates
- 22 tests in `backend/tests/test_capacity.py`

### UI-001: App Shell Layout

- **Files:** `frontend/src/layout/AppShell.tsx`, `HistoryPane.tsx`, `ChatPane.tsx`, `IntelligencePane.tsx`, `TopBar.tsx`, `BottomControls.tsx`
- Four-panel layout: history (left), chat (center), intelligence (right), controls (bottom)
- TDD approach: tests written first in commit `1b8678a`, implementation in `b49e58f`
- 29 tests across 6 layout test files
- **Owner:** `claude-ui`

## Review Findings

- `b30b53a` -- Fix review findings across API-001, DATA-002, OPS-003 (batch fix after initial integration)
- Adapter timeout handling was tightened (`a89dc89`)
- Mandatory doc updates were enforced in task prompts going forward

## Tests Added This Milestone

| Component | Tests |
|-----------|-------|
| Backend (schema, db, event_log, adapters x3, api x2, models, capacity) | ~183 |
| Frontend (layout x6, App) | ~31 |
| **Total** | **~214** |

## What This Unblocked

- DATA-001 + DATA-003 unblocked DATA-004 (checkpoint packer)
- ORCH-001 unblocked ORCH-002 (state machine), ORCH-003 (scheduler), API-004 (agent config)
- API-001 unblocked API-003/004/005
- All three adapters unblocked ADPT-004 (output normalization) and ORCH-004 (batch runner)
- UI-001 unblocked all remaining UI tasks (UI-002 through UI-007)
- GitHub Actions CI was added (`12c1311`) to gate all future PRs

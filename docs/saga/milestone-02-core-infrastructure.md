# Quest 02: The Ten-Headed Hydra

> *The party's most ambitious early quest -- ten tasks across five different guilds, all merged through the first serialized merge queue. The data layer, all three CLI adapters, the API gateway, domain models, capacity monitoring, and the UI shell all came together in one massive push.*

## Quest Objectives

| Task | Guild | Objective | Status |
|------|-------|-----------|--------|
| DATA-001 | Data | SQLite schema v1 (conversations, agents, tasks, runs, checkpoints) | Complete |
| DATA-002 | Data | DatabaseManager bootstrap loader | Complete |
| DATA-003 | Data | JSONL event log writer/reader | Complete |
| ADPT-001 | Adapters | Claude CLI adapter | Complete |
| ADPT-002 | Adapters | Codex CLI adapter | Complete |
| ADPT-003 | Adapters | Ollama memo adapter | Complete |
| API-001 | API | FastAPI app + health endpoints | Complete |
| API-002 | API | Conversation CRUD endpoints | Complete |
| ORCH-001 | Orchestration | Domain models (9 enums, 8 dataclasses) | Complete |
| OPS-003 | Operations | Capacity telemetry snapshot | Complete |
| UI-001 | Frontend | App shell layout (4-panel Slack-style) | Complete |

## The First Merge Queue

Seven branches needed to merge without stepping on each other. The party established the merge coordinator pattern -- one branch at a time, in order:

| Order | Task | Result |
|-------|------|--------|
| 1 | API-001 | Merged |
| 2 | DATA-002 | Merged |
| 3 | OPS-003 | Merged |
| 4 | ORCH-001 | Merged |
| 5 | ADPT-003 | Merged |
| 6 | DATA-003 | Merged |
| 7 | API-002 | Merged |

## Loot Gained

### Data Guild
- **SQLite schema** (`backend/storage/schema.sql`) -- 11 tests
- **DatabaseManager** (`backend/storage/db.py`) -- bootstrap on first connect, connection pooling -- 14 tests
- **JSONL event log** (`backend/storage/event_log.py`) -- append-only with filtering and tail -- 17 tests

### Adapter Guild
- **Claude adapter** (`backend/adapters/claude_adapter.py`) -- established the `BaseAdapter` ABC contract -- 14 tests
- **Codex adapter** (`backend/adapters/codex_adapter.py`) -- same interface, different CLI -- 16 tests
- **Ollama adapter** (`backend/adapters/ollama_adapter.py`) -- neutral memo generator via stdin piping -- 15 tests

### API Guild
- **FastAPI app** (`backend/api/app.py`) -- health check, state endpoint, CORS -- 9 tests
- **Conversation CRUD** (`backend/api/routes/conversations.py`) -- create/read/update/soft-delete/list -- 22 tests

### Orchestration Guild
- **Domain models** (`backend/orchestrator/models.py`) -- the type system for the whole project -- 43 tests

### Operations Guild
- **Capacity telemetry** (`backend/runtime/capacity.py`) -- CPU/RAM/active-run snapshots -- 22 tests

### Frontend Guild
- **App shell** (`frontend/src/layout/`) -- TopBar, HistoryPane, ChatPane, IntelligencePane, BottomControls -- 29 tests

## Traps Encountered

- Adapter timeout handling needed tightening after initial integration
- Batch fix across API-001, DATA-002, OPS-003 caught in review

## Loot Summary

~214 tests (183 backend + 31 frontend). The hydra is slain.

## Map Unlocked

This was the quest that opened up the entire map:
- DATA-001 + DATA-003 --> DATA-004 (checkpoint packer)
- ORCH-001 --> ORCH-002 (state machine), ORCH-003 (scheduler), API-004 (agent config)
- All adapters --> ADPT-004 (output normalization), ORCH-004 (batch runner)
- API-001 --> API-003/004/005
- UI-001 --> all remaining UI quests (UI-002 through UI-007)
- GitHub Actions CI gate added -- no more merging without passing trials

*The dungeon is mapped. Time to start raiding.*

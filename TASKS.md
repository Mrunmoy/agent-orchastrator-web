# Agent Orchestrator Web - Unified Backlog

This is the source-of-truth backlog for current known scope.

## Current State Snapshot
- Done: docs baseline, UI mock (`src/mockup.html`), Nix shell, parallel/handoff scripts, backend package layout, frontend app shell layout, SQLite schema v1, Claude/Codex/Ollama adapter baselines, shared dev commands, FastAPI app + health/state endpoints, DatabaseManager bootstrap loader, capacity telemetry snapshot, domain models (enums + dataclasses), conversation CRUD endpoints, JSONL event log writer/reader, conversation state machine, round-robin scheduler, 20-turn batch runner, adapter output normalization, checkpoint pack builder, agent config endpoints, events stream endpoint, conversation history pane, chat timeline, agent roster editor, orchestration control endpoints, steering note injection, capacity-aware throttle, intelligence pane, merge coordinator queue.
- Not done: composer + run controls (UI-004), run-window controls (UI-007), branch lock policy, notification pipeline, auth, LAN profile, remaining test/doc tasks.

## Definition of Done (per task)
- Design/spec links are updated if behavior changed.
- Tests are added/updated and passing.
- Implementation is merged in small commits.
- Task board status moved to `Done` with evidence note.

## Epic SETUP - Project Foundations
- [x] `SETUP-001` Create backend Python package layout (`backend/`, modules, lint/test config)
- [x] `SETUP-002` Create frontend TypeScript app shell (`frontend/`, build/test/lint)
- [x] `SETUP-003` Add shared dev commands (`make lint`, `make test`, `make run-backend`, `make run-frontend`)

## Epic DATA - Persistence and Context Memory
- [x] `DATA-001` Implement SQLite schema v1 (conversations, agents, tasks, runs, checkpoints)
- [x] `DATA-002` Add migration/bootstrap loader for schema initialization
- [x] `DATA-003` Implement append-only JSONL event log writer/reader
- [x] `DATA-004` Implement checkpoint pack builder with token bounds and summary compaction

## Epic ORCH - Orchestration Core
- [x] `ORCH-001` Implement domain models (Agent, Conversation, Task, RunWindow, Notification)
- [x] `ORCH-002` Implement conversation state machine (`Debate`, `Planning`, `Working`, `NeedsInput`, `Queued`, `Completed`, `Failed`)
- [x] `ORCH-003` Implement round-robin scheduler with strict agent order
- [x] `ORCH-004` Implement 20-turn batch runner with pause/continue/stop-now
- [x] `ORCH-005` Implement user steering note injection between windows
- [x] `ORCH-006` Implement capacity-aware throttle and queue/resume policy

## Epic ADPT - CLI Agent Adapters
- [x] `ADPT-001` Implement Claude CLI adapter (prompt, session attach/resume hooks, timeout handling)
- [x] `ADPT-002` Implement Codex CLI adapter (prompt, session attach/resume hooks, timeout handling)
- [x] `ADPT-003` Implement Ollama memo adapter for neutral decision memo
- [x] `ADPT-004` Normalize adapter output into common message/event schema

## Epic API - Backend Service
- [x] `API-001` Implement FastAPI app with health/config endpoints
- [x] `API-002` Implement conversation CRUD endpoints
- [x] `API-003` Implement orchestration control endpoints (`run`, `continue`, `stop`, `steer`)
- [x] `API-004` Implement agent config endpoints (name, role, personality, order, working dir)
- [x] `API-005` Implement events stream endpoint for UI live updates

## Epic UI - Slack-Like Web Experience
- [x] `UI-001` Implement app shell layout (history left, chat center, intelligence right, controls bottom)
- [x] `UI-002` Implement conversation history list (scroll, select, delete, clear all, status icon)
- [x] `UI-003` Implement chat timeline (avatar, bold name, timestamp, typing/thinking indicator)
- [ ] `UI-004` Implement composer + target-agent routing + run controls
- [x] `UI-005` Implement agent roster editor (unique name, source, model, personality, order)
- [x] `UI-006` Implement intelligence pane (agreement/disagreement + neutral memo)
- [ ] `UI-007` Implement run-window controls (next 20, continue 20, stop now, steering note)

## Epic COORD - Parallel Delivery and Merge Safety
- [x] `COORD-001` Implement merge-coordinator queue model and serialized integration flow
- [x] `COORD-002` Implement branch/task lock policy to avoid multi-agent file conflicts
- [x] `COORD-003` Implement notifications for `Needs Input`, `Blocked`, `Completed`, `Queued`

## Epic TEST - Test and Quality Gates
- [x] `TEST-001` Backend unit tests for scheduler, batch runner, state transitions
- [ ] `TEST-002` Adapter contract tests with mocked CLI responses
- [x] `TEST-003` Frontend component tests for history, timeline, controls
- [ ] `TEST-004` End-to-end scenario: debate -> agreement -> task split -> completion notification

## Epic OPS - Local Network and Security
- [x] `OPS-001` Add local auth token for control APIs and basic request limits
- [ ] `OPS-002` Add LAN run profile and startup scripts for phone/tablet/laptop access
- [x] `OPS-003` Add capacity telemetry snapshot (CPU/RAM/active agent runs) surfaced to UI

## Epic DOC - Living Engineering Record
- [ ] `DOC-001` Add ADR entries for orchestration algorithm and resume strategy
- [ ] `DOC-002` Add playbook templates for debugging and recovery drills
- [ ] `DOC-003` Start project saga log with incremental milestone updates

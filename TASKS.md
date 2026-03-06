# Agent Orchestrator Web - Task Tracker

## Phase 0 - Foundation
- [ ] Create project skeleton (`src/`, `docs/`, `config/`, `tests/`, `scripts/`, `data/`)
- [x] Add `README.md` with quickstart and architecture overview
- [x] Add Nix toolchain (`flake.nix`, optional `.envrc`, `nix develop` workflow)
- [ ] Add Python project bootstrap (`pyproject.toml`)
- [ ] Add `Makefile` targets: `run`, `lint`, `test`, `format`
- [x] Add default personalities config: `config/personalities.json`

## Phase 1 - Core Orchestrator
- [ ] Implement `Agent` model (id, name, kind, session_id, personality_key, order, enabled)
- [ ] Implement `ConversationState` and `WorkflowState`
- [ ] Implement strict round-robin scheduler for N agents
- [ ] Implement directed first-turn routing
- [ ] Implement batch execution (default 20)
- [ ] Implement pause/continue semantics
- [ ] Implement stop-now flag handling

## Phase 2 - Workflow Phases and Gates
- [ ] Implement phases: `DESIGN_DEBATE`, `TDD_PLANNING`, `IMPLEMENTATION`, `INTEGRATION`, `DOCS`, `MERGE`
- [ ] Implement gate state: `OPEN`, `SATISFIED`, `APPROVED`
- [ ] Implement phase transition rules and validation
- [ ] Implement gate approval endpoint/action
- [ ] Surface phase/gate status in UI timeline and header

## Phase 3 - Prompt Contracts and Agreement
- [ ] Define mandatory response markers:
- [ ] `AGREEMENT_STATUS: AGREE|CONTINUE`
- [ ] `PHASE_STATUS: READY_FOR_GATE|NEEDS_MORE_WORK`
- [ ] `NEXT_ACTION: ...`
- [ ] Implement robust parser for these markers
- [ ] Implement all-agree detection logic
- [ ] Implement gate-satisfied detection logic

## Phase 4 - CLI Adapters
- [ ] Implement `CodexAdapter` (`codex exec`, optional `exec resume`, session discovery)
- [ ] Implement `ClaudeAdapter` (`claude -p`, optional `-r/--session-id`)
- [ ] Add optional `OllamaManagerAdapter` scaffold
- [ ] Add per-turn timeout and retry policy
- [ ] Add structured adapter error reporting

## Phase 5 - API Surface
- [ ] `GET /conversations` (history list metadata)
- [ ] `POST /conversations/new`
- [ ] `POST /conversations/select` (build smart resume pack)
- [ ] `POST /conversations/delete`
- [ ] `POST /conversations/clear-all`
- [ ] `POST /moderate` (Ollama manager pass)
- [ ] `POST /summarize` (batch summary generation)
- [ ] `POST /gate-check` (phase gate recommendation)
- [ ] `GET /state`
- [ ] `GET /events?since=`
- [ ] `POST /chat`
- [ ] `POST /continue`
- [ ] `POST /steer`
- [ ] `POST /stop`
- [ ] `POST /phase`
- [ ] `POST /gate/approve`
- [ ] `POST /agents`
- [ ] `POST /settings`
- [ ] `GET /personalities`

## Phase 6 - UI/UX (Group Chat)
- [ ] Left pane conversation history list is scrollable
- [ ] Row actions: rename, delete, and active highlight
- [ ] Global action: clear all conversations (confirmed)
- [ ] No-thread linear conversation UX
- [ ] Batch artifact cards: `Agreements`, `Disagreements`, `Neutral Memo`
- [ ] Disagreement table with per-topic `agent A vs agent B` positions
- [ ] Chat bubble layout with per-agent avatars
- [ ] Typing indicator for current active agent
- [ ] Agent management panel (name/type/session/personality/order)
- [ ] Composer with target-agent selector
- [ ] Batch controls (`Run N`, `Continue N`, `Stop`)
- [ ] Steering/preference controls between batches
- [ ] Phase and gate dashboard
- [ ] Working-directory selector/editor
- [ ] Mobile-first responsive polish

## Phase 7 - TDD Workflow Enforcement Features
- [ ] Add TDD checklist card in `TDD_PLANNING` phase
- [ ] Require test plan artifact before allowing `IMPLEMENTATION` gate approval
- [ ] Add integration evidence checklist before `INTEGRATION` gate approval
- [ ] Add docs evidence checklist before `DOCS` gate approval

## Phase 8 - Memory and Persistence
- [ ] Implement checkpoint save/restore per batch
- [ ] Implement dual resume bootstrap modes (`continue-session`, `reconstruct`)
- [ ] Persist `data/conversations.json` metadata index
- [ ] Implement smart resume context-pack builder
- [ ] Enforce resume token soft/hard caps with truncation strategy
- [ ] Persist batch artifacts (`data/artifacts/*.json`)
- [ ] Persist app state (`data/app_state.json`)
- [ ] Persist transcripts (`data/transcripts/*.jsonl`)
- [ ] Add SQLite index for fast query/filter
- [ ] Add markdown batch summaries (`data/summaries/*.md`)
- [ ] Add transcript export to Markdown

## Phase 9 - Security and LAN Deployment
- [ ] Access-token auth for all control APIs
- [ ] Input/request size limits and sanitization
- [ ] Working-dir validation and safe fallback
- [ ] LAN deployment runbook (phone/tablet/laptop access)
- [ ] Optional systemd user service doc

## Phase 10 - Testing and Hardening
- [ ] Unit tests: scheduler order, batch pause, stop behavior
- [ ] Unit tests: phase/gate transition validation
- [ ] Unit tests: agreement/status parser
- [ ] Validate resume behavior with missing/expired session IDs
- [ ] API tests for orchestration endpoints
- [ ] UI smoke tests for critical flows
- [ ] End-to-end scenario test:
- [ ] debate -> agreement -> TDD plan -> implementation tasks -> integration -> docs -> merge-ready

## Stretch Goals
- [ ] Configurable Ollama moderation policy (`always`, `on_conflict`, `manual`)
- [ ] WebSocket realtime transport
- [ ] Multi-room support
- [ ] Per-agent model override from UI
- [ ] Tool-call timeline and cost tracking


## Phase 11 - Background Execution and Scheduler
- [ ] Implement conversation state machine (`Debate`, `Planning`, `Autonomous Work`, `Needs User Input`, `Completed`, `Failed`, `Queued`)
- [ ] Implement auto-throttle scheduler using machine metrics + agent availability
- [ ] If capacity unavailable, block start and queue notification for resource-free event
- [ ] Implement resource-free notifier for queued conversations
- [ ] Implement role split: worker agents vs single merge coordinator
- [ ] Enforce serialized integration/merge pipeline with user-gated main merge
- [ ] Allow unrelated subtasks to continue when one branch needs clarification
- [ ] Enforce completion criteria (tasks + tests + docs + integration + user sign-off)
- [ ] Implement notification priority ordering in history pane

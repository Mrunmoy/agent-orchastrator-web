# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent orchestration web app for running local CLI agents (Claude, Codex, Ollama) in structured debate-to-agreement workflows. Local-first, LAN-accessible. Not just a chat UI — it's an engineering cockpit with phased execution (design debate -> TDD -> implementation -> integration -> docs -> merge).

## Dev Environment

Always use `nix develop` to enter the dev shell. It provides Python 3.12, Node.js 22, and all tooling. Frontend deps auto-bootstrap on shell entry; if not, run `npm ci --prefix frontend`.

## Common Commands

```bash
# Enter dev shell (required)
nix develop

# Backend
cd backend && pytest -q                      # run all backend tests
cd backend && pytest tests/test_schema.py -q  # run a single test file
cd backend && ruff check src/ tests/          # lint
cd backend && black --check src/ tests/       # format check

# Frontend
cd frontend && npm test                       # run all frontend tests (vitest)
cd frontend && npx vitest run src/layout/AppShell.test.tsx  # single test file
cd frontend && npm run lint                   # eslint
cd frontend && npm run format:check           # prettier check
cd frontend && npm run dev                    # vite dev server
cd frontend && npm run build                  # tsc + vite build

# Project-level (from repo root)
make serve          # static server on :8080
make test-ui        # Playwright smoke test on mockup
make ui-shot        # capture mockup screenshot
make verify         # test-ui + ui-shot
```

## Architecture

### Monorepo Layout

- **`backend/`** — Python (FastAPI + uvicorn). Package: `agent_orchestrator` under `backend/src/`. Tests: `backend/tests/`.
- **`frontend/`** — TypeScript + React 19, Vite, Vitest + Testing Library. Source: `frontend/src/`.
- **`config/`** — `tasks.json` (machine-readable task registry), `personalities.json` (agent personality profiles).
- **`docs/specs/`** — Numbered implementation contracts (01-top-bar through 12-domain-model).
- **`docs/coordination/`** — `task-board.md` for task tracking, parallel workflow docs.
- **`TASKS.md`** — Unified backlog (epics: SETUP, DATA, ORCH, ADPT, API, UI, COORD, TEST, OPS, DOC).

### Backend Modules (`backend/src/agent_orchestrator/`)

- **`adapters/`** — CLI agent adapters. `BaseAdapter` ABC defines `send_prompt`, `resume_session`, `is_available`. Concrete: `claude_adapter.py`, `codex_adapter.py`.
- **`orchestrator/`** — Batch execution engine, round-robin scheduling, phase/gate state machine (planned).
- **`storage/`** — SQLite persistence, JSONL event log, checkpoint builder (planned).
- **`api/`** — FastAPI routes under `api/routes/`.
- **`runtime/`** — Capacity-aware scheduler, resource monitoring (planned).

### Frontend Layout (`frontend/src/`)

Slack-like four-zone layout implemented in `layout/`:
- `TopBar` — app header
- `HistoryPane` — left sidebar, conversation list
- `ChatPane` — center, chat timeline
- `IntelligencePane` — right sidebar, agreement/disagreement/memo cards
- `BottomControls` — composer, steering, run controls

All layout components exported from `layout/index.ts`, composed in `AppShell.tsx`.

### Key Design Patterns

- **Adapter pattern** for CLI agents — each agent type implements `BaseAdapter`
- **Checkpoint-first resume** — conversations resume from compact context packs, not full transcript replay
- **Batch execution model** — agents run in 20-turn batches, then pause for user steering
- **Phase/gate workflow** — six phases (Design Debate -> TDD Planning -> Implementation -> Integration -> Docs -> Merge), each with gate approval

## Coding Standards

- **Python**: PEP 8, type hints required, `ruff` + `black` formatting. Line length 99. Target Python 3.11+.
- **TypeScript**: strict mode, ESLint + Prettier. Small testable components.
- **Commits**: small, single-purpose.

## Workflow

- Development follows: design doc -> tests -> implementation -> integration test -> docs update.
- Task-driven development using `TASKS.md` backlog and `docs/coordination/task-board.md`.
- Workers never merge directly to `master`. Single merge coordinator handles integration.
- Task board statuses: `Todo -> In Progress -> Review -> Done`.

## Worktree-Based Parallel Development

Tasks are developed in isolated git worktrees:
```bash
make task-worktree TASK_ID=UI-002 PREFIX=claude   # create worktree + branch
make task-ready TASK_ID=UI-002 PREFIX=claude WORKER=claude-ui  # worktree + TASK_PROMPT.md
make task-shell TASK_ID=UI-002 PREFIX=claude WORKER=claude-ui  # above + enter shell
```
Worktrees land in `../agent-orchestrator-worktrees/<task-slug>`. Each gets a `.agent-context.md` with task scope.

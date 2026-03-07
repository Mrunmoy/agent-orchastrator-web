# AGENTS.md

## Purpose
Guidelines for human/AI contributors working on `agent-orchestrator-web`.

## Project Goal
Build a local-first, multi-agent orchestration web app that:
- runs CLI agents (Codex/Claude/Ollama) on local workspaces,
- supports structured debate to agreement,
- supports phased execution (batch runs, pause/continue, steering notes),
- supports background multi-conversation operation with resource-aware scheduling.

## Working Style
- Use small, single-purpose commits.
- Follow: design doc -> tests -> implementation -> integration test -> docs/playbook update.
- Keep modules cohesive and responsibilities separated.
- Prefer explicit interfaces and predictable data contracts.

## Tech Stack
- Frontend: TypeScript + React.
- Backend/Orchestrator: Python.
- Persistence: SQLite (WAL mode) for metadata/state.
- Event stream: append-only JSONL event log.
- Dev environment: Nix (`nix develop`).

## Coding Standards
- C++ (if used): Google C++ style with these project overrides:
  - class members use `m_` prefix,
  - braces on next line (Allman-like).
- Python: PEP 8 + type hints, `ruff` + `black`.
- TypeScript: strict mode, ESLint + Prettier, clear component boundaries.
- Prefer design patterns where they simplify orchestration complexity (state machine, strategy, adapter, queue/worker).

## UI Direction
- Slack-like layout and interaction model:
  - left: conversation history + status icons,
  - middle: chat stream (avatar, name, timestamp, message),
  - right: orchestration/decision pane,
  - bottom: controls and steering input.
- Keep readability first; avoid low-contrast color combinations.

## Orchestration Rules (Current)
- Run in user-triggered batches (default 20 turns), then pause.
- User can inject steering notes between batches.
- Agents reply in configured round-robin order.
- Auto-throttle based on local system capacity and agent availability.
- If capacity unavailable: queue and notify when resources free up.
- Single merge coordinator controls integration/merge progression.

## Persistence and Resume
- Resume via checkpoint summary, not raw transcript replay.
- Session IDs are optional hints, not the sole resume mechanism.
- Keep context token-bounded; include only relevant state slices.

## Definition of Done
A feature is done when all items in `docs/checklists/slice-checklist.md` are checked.

Summary:
- Design doc exists as **HTML** in `docs/design/` (gold theme),
- Failing tests written first (TDD), then implementation,
- `make test`, `make lint`, `make format-check` all pass,
- Playbook entry exists as **HTML** in `docs/playbook/` (teal theme),
- Saga chapter exists as **HTML** in `docs/saga/` (rose theme, **narrative/storytelling voice**),
- All three index.html files updated with links to new docs,
- Tracking files updated: `TASKS.md`, `docs/coordination/task-board.md`, `config/tasks.json`.

## Mandatory Workflow Order
See `docs/WORKFLOW.md` for the full contract. In brief:
1. Design doc (HTML) → 2. Failing tests → 3. Implement → 4. Verify (`make test/lint/format-check`) → 5. Playbook (HTML) → 6. Saga (HTML, narrative voice) → 7. Update indexes → 8. Update tracking files

## Doc Format Rules
- **All design, playbook, and saga docs are HTML** — never markdown.
- Design: gold theme (`--gold:#d6b164`). Playbook: teal theme (`--teal:#62d7c8`). Saga: rose theme (`--rose:#ffa3bf`).
- Saga chapters tell a **story** — like a D&D campaign log. Technical details go in design/playbook.
- Copy CSS from existing HTML files in each directory.

## Quick Commands
- Enter dev shell: `nix develop`
- Run all tests: `make test`
- Run backend tests only: `make test-backend`
- Run frontend tests only: `make test-frontend`
- Lint all: `make lint`
- Format check: `make format-check`
- Run backend dev server: `make run-backend`
- Run frontend dev server: `make run-frontend`

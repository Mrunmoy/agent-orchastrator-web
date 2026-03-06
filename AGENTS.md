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
A feature is done when:
- design doc exists/updated,
- unit + integration tests pass,
- docs/specs updated,
- playbook notes added for key decisions/debug findings,
- UI behavior matches agreed workflow.

## Quick Commands
- Enter dev shell: `nix develop`
- Run mock UI: `make mockup`
- Capture mock screenshot: `make capture-mock`
- Run UI tests: `make test-ui`
- Run all checks: `make check`

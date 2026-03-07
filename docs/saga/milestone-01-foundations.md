# Milestone 01: Project Foundations

## Summary

The foundations milestone established the development environment, backend package layout, frontend app shell, and shared developer commands. This phase set the rules for everything that followed: Nix for reproducibility, TDD as mandatory practice, and git worktrees for parallel task execution.

## Timeline

All foundation work landed on `main` via direct branch merges before the PR-based workflow was introduced.

| Commit | Task | Description |
|--------|------|-------------|
| `61e5cbc` | -- | Initialize dev environment and project scaffolding |
| `712147e` | -- | Add parallel multi-agent handoff and coordination workflow |
| `99d9044` | -- | Add task-id based worktree provisioning workflow |
| `136bb1d` | SETUP-001 | Add backend Python package layout with lint/test config |
| `f8ec0b2` | SETUP-002 | Add frontend TypeScript app shell with React, Vite, and test setup |
| `ce559ca` | SETUP-003 | Add shared dev commands to root Makefile |

## What Was Built

### SETUP-001: Backend Python Package Layout

- **Scope:** `backend/`
- Created the Python package structure: `backend/api/`, `backend/adapters/`, `backend/orchestrator/`, `backend/storage/`, `backend/runtime/`
- Added lint configuration (ruff/flake8) and test configuration (pytest)
- `backend/tests/test_package_layout.py` -- 7 tests verifying module imports
- **Owner:** `claude-backend`

### SETUP-002: Frontend TypeScript App Shell

- **Scope:** `frontend/`
- Bootstrapped React + TypeScript + Vite project
- Configured Vitest for component testing
- `frontend/src/App.test.tsx` -- 2 smoke tests
- **Owner:** `claude-frontend`

### SETUP-003: Shared Dev Commands

- **Scope:** `Makefile`, `scripts/`
- Root `Makefile` with targets: `make lint`, `make test`, `make run-backend`, `make run-frontend`
- Later extended with `make test-api`, `make test-integration`, `make test-all`
- `tests/test_dev_commands.py` -- validates Makefile targets exist
- **Owner:** unassigned (completed as part of foundation sweep)

## Infrastructure Decisions

- **Nix dev shell** (`flake.nix`) pins Python, Node, and all tooling versions. Every agent enters the same environment via `nix develop`.
- **Worktree provisioning** -- `scripts/` contains task-prompt generators that create isolated git worktrees per task ID, enabling parallel execution.
- **Branch namespace prefixes** -- parallel sub-agents use `claude/`, `codex/` prefixes to avoid branch collisions.

## Tests Added

- 7 backend package layout tests
- 2 frontend smoke tests
- 1 dev commands test
- **Total: ~10 tests**

## What This Unblocked

Every subsequent task depends on SETUP-001 or SETUP-002. The backend layout enabled all DATA, ORCH, ADPT, API, and OPS tasks. The frontend shell enabled all UI tasks. The shared Makefile enabled CI (GitHub Actions was added in commit `12c1311`).

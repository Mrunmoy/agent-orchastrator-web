# Feature Design: SETUP-003 Shared Dev Commands

## Context
- Problem: No unified Makefile targets for lint, test, format-check, or running backend/frontend dev servers. Developers must remember per-directory commands.
- Scope: Add `make lint`, `make test`, `make format-check`, `make run-backend`, `make run-frontend` to root Makefile.
- Non-goals: CI pipeline integration, pre-commit hooks, watch modes.

## Requirements
- Functional:
  - `make test` runs both backend (pytest) and frontend (vitest) tests.
  - `make lint` runs ruff + eslint across both stacks.
  - `make format-check` runs black --check + prettier --check.
  - `make run-backend` starts uvicorn dev server.
  - `make run-frontend` starts vite dev server.
  - Each sub-target also works independently (e.g. `make test-backend`, `make test-frontend`).
- Non-functional:
  - Targets fail fast with clear error output.
  - All commands assume `nix develop` shell.

## Proposed Design
- Add targets to existing root `Makefile`.
- Backend commands run from `backend/` directory.
- Frontend commands run from `frontend/` directory using npm scripts.
- Aggregate targets (`test`, `lint`, `format-check`) run both stacks sequentially.

## Alternatives Considered
1. npm workspaces / monorepo tool (unnecessary overhead for two packages).
2. Shell script wrapper (Makefile already established as the project runner).

## Test Strategy
- Integration: a test script that verifies each make target exits 0 on the current codebase.

## Acceptance Criteria
- [ ] `make test` runs backend + frontend tests and exits 0
- [ ] `make lint` runs ruff + eslint and exits 0
- [ ] `make format-check` runs black --check + prettier --check and exits 0
- [ ] `make run-backend` starts uvicorn
- [ ] `make run-frontend` starts vite dev server
- [ ] Help target updated with new commands

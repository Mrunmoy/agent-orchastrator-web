# Saga Chapter 1: Project Foundations

## Arc Summary
- Completed SETUP epic: backend package layout, frontend app shell, and shared dev commands.

## What We Built
- SETUP-001: Backend Python package with adapters, orchestrator, storage, runtime, api modules
- SETUP-002: Frontend TypeScript app shell with Slack-like four-zone layout
- SETUP-003: Unified Makefile targets for test, lint, format-check, run-backend, run-frontend

## Challenges Faced
- Pre-existing lint/format violations surfaced when adding shared check targets
- Adapter code used deprecated asyncio.TimeoutError alias (ruff UP041)
- SQL string literals in schema tests exceeded line-length limit

## Breakthroughs
- All lint, format, and test checks now pass from a single command (`make test`, `make lint`, `make format-check`)
- Foundation is solid for parallel development across backend and frontend

## Evidence
- 12/12 SETUP-003 dev command tests pass
- 5 backend tests pass (pytest)
- 36 frontend tests pass (vitest)

## Next Quest
- ORCH-001: Domain models
- API-001: FastAPI app + health endpoint
- Then: orchestration loop, conversation CRUD, and UI features

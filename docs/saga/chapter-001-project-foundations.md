# Saga Chapter 1: Project Foundations

## Arc Summary
- Completed SETUP epic: backend package layout, frontend app shell, and shared dev commands.
- Completed first parallel sprint: FastAPI health API, DatabaseManager bootstrap, capacity telemetry.

## What We Built

### SETUP Epic
- SETUP-001: Backend Python package with adapters, orchestrator, storage, runtime, api modules
- SETUP-002: Frontend TypeScript app shell with Slack-like four-zone layout
- SETUP-003: Unified Makefile targets for test, lint, format-check, run-backend, run-frontend

### Parallel Sprint: API-001, DATA-002, OPS-003
- API-001: FastAPI app factory with `/health` and `/state` endpoints, shared envelope helpers (`ok_response`/`error_response`)
- DATA-002: DatabaseManager with schema bootstrap from `schema.sql`, `PRAGMA user_version` tracking, WAL mode, context manager protocol
- OPS-003: Capacity telemetry via psutil — CPU load, RAM usage, configurable threshold gates, `CapacitySnapshot`/`CapacityVerdict` dataclasses

## Challenges Faced
- Pre-existing lint/format violations surfaced when adding shared check targets
- Adapter code used deprecated asyncio.TimeoutError alias (ruff UP041)
- SQL string literals in schema tests exceeded line-length limit
- Parallel agents left work uncommitted in worktrees — merge coordinator had to copy and commit manually
- `executescript()` resets `PRAGMA foreign_keys` — required re-enabling after schema load
- API envelope pattern needed extraction to shared module to avoid duplication across future routes

## Breakthroughs
- All lint, format, and test checks now pass from a single command (`make test`, `make lint`, `make format-check`)
- First successful three-way parallel development with worktree isolation and serialized merge queue
- 112 backend tests + 36 frontend tests all green after merge

## Evidence
- 12/12 SETUP-003 dev command tests pass
- 9 API health endpoint tests pass
- 14 DatabaseManager tests pass
- 22 capacity telemetry tests pass
- 36 frontend tests pass (vitest)

## Next Quest
- ORCH-001: Domain models (unblocked — depends on SETUP-001, DATA-001, both Done)
- ORCH-002/003: State machine and scheduler
- API-002: Conversation CRUD endpoints
- Then: batch runner, orchestration controls, and UI features

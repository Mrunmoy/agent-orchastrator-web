# Playbook Entry: SETUP-003 Shared Dev Commands

## Date
2026-03-07

## Context
- Area/module: Root Makefile, project-wide dev tooling
- Trigger: No unified lint/test/run commands existed; developers had to remember per-directory commands

## Symptoms
- Pre-existing formatting violations (black) in 4 backend files from earlier adapter work
- Pre-existing ruff UP041 lint errors (asyncio.TimeoutError alias) in adapter code
- Prettier violation in frontend ChatPane.tsx
- Long SQL string literals in test_schema.py exceeding 99-char line limit

## Root Cause
- Earlier tasks (ADPT-001, ADPT-002, DATA-001) were merged without running project-wide lint/format checks (because those targets didn't exist yet)

## Resolution
- Added Makefile targets: test, test-backend, test-frontend, lint, lint-backend, lint-frontend, format-check, run-backend, run-frontend
- Fixed all ruff/black/prettier violations across backend and frontend
- Extracted _INSERT_MSG_EVENT constant in test_schema.py to resolve line-length issues

## Verification
- Tests/evidence: 12/12 tests in tests/test_dev_commands.py pass; all backend (pytest) and frontend (vitest) tests green

## Preventive Actions
- `make lint` and `make format-check` should be run before merging any branch going forward

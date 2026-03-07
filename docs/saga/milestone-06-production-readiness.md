# Milestone 06: Production Readiness (Batch 4 Parallel Delivery)

## Summary

The fourth and final parallel batch addressed production hardening: the last P0 UI component (composer + run controls), branch/task lock policy to prevent multi-agent file conflicts, a notification pipeline, local auth with rate limiting, and adapter contract tests. This batch also introduced mandatory tracking document updates in every agent prompt, ensuring the task board, TASKS.md, and tasks.json stay synchronized.

## Timeline

These tasks are on feature branches, pending PR creation and merge to `main`.

| Branch | Task | Status |
|--------|------|--------|
| `claude/ui-004-composer-controls` | UI-004 | Branch ready |
| `claude/coord-002-task-locks` | COORD-002 | Branch ready |
| `claude/coord-003-notifications` | COORD-003 | Branch ready |
| `claude/ops-001-auth-limits` | OPS-001 | Branch ready |
| `claude/test-002-adapter-contracts` | TEST-002 | Branch ready |

### Branch Commits

| Commit | Task | Description |
|--------|------|-------------|
| `554a05c` | UI-004 | Add composer and run controls components |
| `a5c55a5` | COORD-002 | Add branch/task lock policy |
| `940411b` | COORD-003 | Add notification pipeline |
| `b27a5b8` | OPS-001 | Add local auth token and rate limiter |
| `a14f1cd` | TEST-002 | Add adapter contract tests |

## What Was Built

### UI-004: Composer + Run Controls

- **Scope:** `frontend/src/features/composer/`
- Message composer with target-agent routing (send to specific agent or broadcast)
- Run controls: start batch, continue, stop now
- This was the last P0 task in the UI epic, completing the core user interface
- Tests: `Composer.test.tsx`, `RunControls.test.tsx`

### COORD-002: Branch/Task Lock Policy

- **Scope:** `backend/orchestrator/locks.py`
- Prevents multiple agents from working on overlapping file scopes simultaneously
- Lock acquisition, release, and deadlock prevention
- Tests: `backend/tests/test_locks.py`

### COORD-003: Notification Pipeline

- **Scope:** `backend/runtime/notifications.py`
- Notifications for state changes: `NeedsInput`, `Blocked`, `Completed`, `Queued`
- Pluggable delivery (in-app, webhook-ready)
- Tests: `backend/tests/test_notifications.py`

### OPS-001: Local Auth Token and Rate Limiting

- **Scope:** `backend/api/security.py`
- Bearer token authentication for control APIs
- Request rate limiting to prevent abuse on LAN deployments
- Tests: `backend/tests/test_security.py`

### TEST-002: Adapter Contract Tests

- **Scope:** `backend/tests/test_adapter_contracts.py`
- Contract tests verify all three adapters (Claude, Codex, Ollama) conform to `AdapterBase`
- Mocked CLI responses ensure tests run without actual CLI installations
- Validates response format, error handling, timeout behavior across all adapters

## Process Change: Mandatory Tracking Updates

Starting with this batch, every agent prompt includes explicit instructions to update all three tracking documents as part of the commit:

1. `TASKS.md` -- checkbox status
2. `docs/coordination/task-board.md` -- row status, owner, branch
3. `config/tasks.json` -- status field

This was introduced after earlier batches showed drift between the tracking files. The rule ensures the project record stays accurate as a side effect of normal development.

## Cumulative Test Summary (All Milestones)

| Milestone | Backend Tests | Frontend Tests | Total |
|-----------|--------------|----------------|-------|
| 01 - Foundations | ~9 | ~2 | ~10 |
| 02 - Core Infrastructure | ~183 | ~31 | ~214 |
| 03 - Orchestration Engine | ~51 | ~19 | ~70 |
| 04 - Execution Runtime | ~37 | ~19 | ~56 |
| 05 - Coordination Layer | ~79 | ~14 | ~93 |
| 06 - Production Readiness | (on branches) | (on branches) | (pending) |
| **On main as of PR #15** | **~340** | **~88** | **~430+** |

## What Remains

After Batch 4 merges, the remaining backlog items are:

- **UI-007** -- Run-window controls and steering (depends on ORCH-005, UI-004)
- **TEST-001** -- Orchestrator unit tests (scheduler, batch runner, state transitions)
- **TEST-003** -- Frontend component tests (history, timeline, controls)
- **TEST-004** -- End-to-end scenario test
- **OPS-002** -- LAN run profile and startup scripts
- **DOC-001** -- ADR entries for orchestration algorithm and resume strategy
- **DOC-002** -- Playbook templates for debugging and recovery drills
- **DOC-003** -- Project saga log (this document)

The system is functionally complete for local single-user orchestration. Remaining work focuses on test depth, operational tooling, and documentation.

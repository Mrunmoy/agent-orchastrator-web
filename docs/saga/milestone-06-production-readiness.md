# Quest 06: Fourth Raid -- Fortifying the Keep

> *The party shifts from building to hardening. The last P0 UI component (composer + run controls) completes the interface. Branch locks prevent agents from trampling each other's work. A notification pipeline alerts the Dungeon Master to state changes. Auth and rate limiting protect the gates. And 67 adapter contract tests ensure every adapter honors the same code of conduct. This is also the raid where the party finally starts tracking their kills properly.*

## Raid Composition

| PR | Task | Objective | Tests |
|----|------|-----------|-------|
| #17 | COORD-003 | Notification pipeline | 23 |
| #18 | COORD-002 | Branch/task lock policy | 21 |
| #19 | OPS-001 | Local auth token + rate limiter | 16 |
| #20 | UI-004 | Composer + run controls (last P0!) | 23 |
| #21 | TEST-002 | Adapter contract tests | 67 |

## Loot Gained

### UI-004: Composer + Run Controls (Final P0)
- **Drop:** `frontend/src/features/composer/`
- Composer: textarea with agent-targeting dropdown (send to one or broadcast), Enter-to-send, disabled state
- RunControls: status-aware buttons (Run when idle, Continue when paused, Stop when running), steering note input
- **This was the last P0 task.** The core UI is now complete.

### COORD-002: Branch/Task Lock Policy
- **Drop:** `backend/orchestrator/locks.py`
- Three lock types: BRANCH, FILE, TASK -- independent namespaces
- LockManager: acquire (idempotent for same owner), release (owner-only, type-specific), TTL expiry
- LockConflictError with clear resource/owner/existing_owner info

### COORD-003: Notification Pipeline
- **Drop:** `backend/runtime/notifications.py`
- Five notification types: NEEDS_INPUT, BLOCKED, COMPLETED, QUEUED, ERROR
- Pipeline: emit --> dispatch to handlers --> store in history
- LoggingHandler for in-memory storage, pluggable handler protocol

### OPS-001: Auth + Rate Limiter
- **Drop:** `backend/api/security.py`
- TokenValidator: disabled by default (local-first), constant-time comparison when enabled
- RateLimiter: sliding-window per-client, configurable RPM
- generate_token(): `secrets.token_urlsafe(32)`
- Building blocks only -- middleware wiring is a future quest

### TEST-002: Adapter Contract Tests
- **Drop:** `backend/tests/test_adapter_contracts.py`
- 67 tests across 8 test classes verifying Claude, Codex, and Ollama all honor the BaseAdapter contract
- Covers: subclass conformance, send_prompt/resume_session/is_available contracts, timeout handling, error handling, normalize integration, cross-adapter consistency
- All CLI calls mocked -- no real tools needed to run

## Traps and Review Findings

| Trap | What Went Wrong | Fix |
|------|----------------|-----|
| Ambiguous release | `LockManager.release` only took resource name, not lock type. Releasing a TASK lock could accidentally kill a FILE lock on the same resource name. | `release` now requires `lock_type` parameter, keyed by `(lock_type, resource)` |

## Process Change: The Quest Log Rule

Starting with this raid, every agent prompt includes mandatory instructions to update all three tracking documents as part of their commit:

1. `TASKS.md` -- checkbox status
2. `docs/coordination/task-board.md` -- row status, owner, branch
3. `config/tasks.json` -- status field

This was introduced because the party realized nobody had been updating the quest log for the first three raids. The Dungeon Master was not amused.

## Loot Summary

149 tests (127 backend + 22 frontend). The adapter contract tests alone are 67 -- the single largest test file.

## Cumulative Campaign Loot

| Quest | Backend | Frontend | Total |
|-------|---------|----------|-------|
| 01 - Foundation Stones | ~9 | ~2 | ~10 |
| 02 - Ten-Headed Hydra | ~183 | ~31 | ~214 |
| 03 - The Engine Room | ~51 | ~19 | ~70 |
| 04 - The Batch Forge | ~37 | ~19 | ~56 |
| 05 - The War Room | ~79 | ~14 | ~93 |
| 06 - Fortifying the Keep | ~127 | ~22 | ~149 |
| **Grand Total** | **~486** | **~107** | **~590+** |

## Remaining Quests

| Task | Description | Blocked By |
|------|-------------|------------|
| UI-007 | Run-window controls and steering UI | UI-004 (done), ORCH-005 (done) -- ready to go |
| OPS-002 | LAN run profile and startup scripts | Nothing -- ready |
| TEST-004 | End-to-end scenario test | COORD-003 (done), UI-004 (done) -- ready |

The system is functionally complete for local single-user orchestration. What remains is the run-window UI, LAN deployment tooling, and the big integration test.

*The keep is fortified. The gates are guarded. The quest log is finally being maintained. The party surveys their domain from the battlements -- it's been a hell of a campaign.*

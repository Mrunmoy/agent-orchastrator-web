# Quest 01: The Foundation Stones

> *Before you can slay dragons, you need a campsite. The party lays down the Nix shell, the backend package layout, and the frontend app shell -- the three foundation stones upon which everything else will be built.*

## Quest Objectives

| Task | Objective | Status |
|------|-----------|--------|
| SETUP-001 | Establish the backend Python stronghold | Complete |
| SETUP-002 | Raise the frontend TypeScript watchtower | Complete |
| SETUP-003 | Forge shared dev commands in the Makefile anvil | Complete |

## Loot Gained

### SETUP-001: The Backend Stronghold
- **Location:** `backend/`
- Created the module structure: `api/`, `adapters/`, `orchestrator/`, `storage/`, `runtime/`
- Added lint (ruff) and test (pytest) configuration
- 7 tests verifying all modules import correctly

### SETUP-002: The Frontend Watchtower
- **Location:** `frontend/`
- React + TypeScript + Vite, with Vitest for testing
- 2 smoke tests to prove the watchtower stands

### SETUP-003: The Makefile Anvil
- **Location:** `Makefile`, `scripts/`
- Targets: `make lint`, `make test`, `make run-backend`, `make run-frontend`
- 1 test validating targets exist

## Key Decisions Made at Camp

- **Nix dev shell** (`flake.nix`) -- every party member enters the same environment. No "works on my machine" excuses.
- **Git worktrees** -- the party can split up and work in parallel dungeons without merge conflicts.
- **Branch namespaces** -- `claude/` and `codex/` prefixes keep everyone's branches separate.

## Loot Summary

~10 tests total. Not much treasure yet, but the campsite is solid.

## Map Unlocked

Every single future quest depends on these three foundation stones. SETUP-001 unlocks all backend work (DATA, ORCH, ADPT, API, OPS). SETUP-002 unlocks all frontend work (UI). The Makefile enables CI via GitHub Actions.

*The party has a base camp. Time to start exploring.*

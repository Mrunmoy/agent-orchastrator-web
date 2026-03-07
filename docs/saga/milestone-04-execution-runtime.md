# Quest 04: Second Raid -- The Batch Forge

> *The party descends into the forge to build the core execution engine. The 20-turn batch runner -- the heart of the whole system -- is forged here, along with the checkpoint packer, output normalization, and two UI components. Two traps spring during review, both caught before they can do real damage.*

## Raid Composition

| PR | Task | Objective | Tests |
|----|------|-----------|-------|
| #6 | ADPT-004 | Adapter output normalization | 13 |
| #7 | DATA-004 | Checkpoint pack builder | 13 |
| #8 | ORCH-004 | 20-turn batch runner | 11 |
| #9 | UI-003 | Chat timeline | 10 |
| #10 | UI-005 | Agent roster editor | 9 |

## Loot Gained

### ORCH-004: The Batch Runner (Boss Drop)
- **Drop:** `backend/orchestrator/batch_runner.py`
- Drives agent conversations in 20-turn windows
- Pause/continue/stop controls checked between turns (not mid-turn -- intentional design)
- Records every turn as a TurnRecord with agent ID, prompt, response, status, timestamp
- Adapter errors don't crash the batch -- they're recorded as ERROR status and the batch continues

### ADPT-004: Output Normalization
- **Drop:** `backend/adapters/normalize.py`
- Converts raw adapter output into `NormalizedMessage` schema
- Status mapping: IDLE/RUNNING --> "ok", TIMED_OUT --> "timeout", ERROR --> "error"
- All adapters now speak the same language

### DATA-004: Checkpoint Packer
- **Drop:** `backend/storage/checkpoint.py`
- Token-bounded context packs for conversation resume
- Two-phase compaction: drop oldest events first, then truncate summary if still over limit
- Token estimation: `words * 1.3`

### UI-003: Chat Timeline
- **Drop:** `frontend/src/features/chat/`
- ChatMessage (avatar, name, timestamp, thinking dots) + ChatTimeline (scrollable, auto-scroll, empty state)

### UI-005: Agent Roster Editor
- **Drop:** `frontend/src/features/agents/`
- AgentCard (status dot, provider badge, role badge, edit button) + AgentRoster (grid, add button, empty state)

## Traps and Review Findings

| Trap | What Went Wrong | Fix |
|------|----------------|-----|
| Unguarded adapter lookup | `self._adapter_map[agent.id]` was outside the try block -- a missing adapter would crash the entire batch instead of recording an error | Moved inside try, added finally for agent status reset, added `test_missing_adapter_mapping_records_error` |
| Missing button types | Buttons in AgentRoster and AgentCard lacked `type="button"` -- inside a form, they'd trigger unintended submission | Added `type="button"` to both |

## Loot Summary

56 tests (37 backend + 19 frontend).

## Map Unlocked

ORCH-004 was the critical-path boss. Defeating it unlocked:
- ORCH-005 (steering notes) -- inject user guidance between batch windows
- ORCH-006 (capacity throttle) -- queue/resume policy
- API-003 (orchestration control endpoints) -- the API to drive it all
- COORD-001 (merge coordinator queue) -- serialized integration model

DATA-004 means long conversations can resume from checkpoints instead of replaying everything.

*The forge is lit. The batch runner hums with power. The party can now orchestrate agents for real.*

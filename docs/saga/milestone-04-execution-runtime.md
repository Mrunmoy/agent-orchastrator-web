# Milestone 04: Execution Runtime (Batch 2 Parallel Delivery)

## Summary

The second parallel batch delivered the execution runtime: the 20-turn batch runner that actually drives agent conversations, the checkpoint packer for context management, adapter output normalization for a unified message schema, and two UI components (chat timeline and agent roster). Five tasks ran in worktrees, producing PRs #6 through #10.

## Timeline

| PR | Branch | Task | Merge Commit |
|----|--------|------|-------------|
| #6 | `claude/adpt-004-output-normalization` | ADPT-004 | `3ae290a` |
| #7 | `claude/data-004-checkpoint-packer` | DATA-004 | `058f519` |
| #8 | `claude/orch-004-batch-runner` | ORCH-004 | `263c69b` |
| #9 | `claude/ui-003-chat-timeline` | UI-003 | `b9cf6b9` |
| #10 | `claude/ui-005-agent-roster` | UI-005 | `07e8e40` |

### Review Fix Commits

| Commit | Fix |
|--------|-----|
| `15f22a4` | Guard adapter lookup inside try block, add missing-adapter test |
| `207b642` | Add `type="button"` to prevent unintended form submission |

## What Was Built

### ADPT-004: Adapter Output Normalization

- **File:** `backend/adapters/normalize.py`
- Converts raw adapter output (Claude JSON, Codex text, Ollama structured) into a common `NormalizedMessage` schema
- Handles edge cases: missing fields, unexpected formats, encoding issues
- **Review finding:** Adapter lookup was not guarded in a try block. When an unknown adapter name was passed, it crashed with a `KeyError` instead of returning a clear error. Fixed in `15f22a4` with a missing-adapter test added.
- 13 tests in `backend/tests/test_normalize.py`

### DATA-004: Checkpoint Pack Builder

- **File:** `backend/storage/checkpoint.py`
- Packs conversation context into token-bounded checkpoints
- Summary compaction when context exceeds token limits
- Supports resume from checkpoint for long-running conversations
- 13 tests in `backend/tests/test_checkpoint.py`

### ORCH-004: 20-Turn Batch Runner

- **File:** `backend/orchestrator/batch_runner.py`
- Drives conversations in 20-turn windows with pause/continue/stop-now controls
- Coordinates with scheduler to determine next agent
- Uses adapter normalization for consistent message handling
- 11 tests in `backend/tests/test_batch_runner.py`

### UI-003: Chat Timeline

- **Files:** `frontend/src/features/chat/ChatTimeline.tsx`, `ChatMessage.tsx`
- Avatar display, bold agent name, timestamp formatting
- Typing/thinking indicator for active agents
- **Review finding:** Buttons in the timeline needed explicit `type="button"` to prevent unintended form submission in parent forms. Fixed in `207b642`.
- 10 tests across `ChatTimeline.test.tsx` (3) and `ChatMessage.test.tsx` (7)

### UI-005: Agent Roster Editor

- **Files:** `frontend/src/features/agents/AgentRoster.tsx`, `AgentCard.tsx`
- Edit unique agent name, source (Claude/Codex/Ollama), model, personality prompt, turn order
- Card-based layout with inline editing
- 9 tests across `AgentRoster.test.tsx` (3) and `AgentCard.test.tsx` (6)

## Tests Added This Batch

| Component | Tests |
|-----------|-------|
| Output normalization | 13 |
| Checkpoint packer | 13 |
| Batch runner | 11 |
| Chat timeline (frontend) | 10 |
| Agent roster (frontend) | 9 |
| **Total** | **56** |

## What This Unblocked

- ORCH-004 (batch runner) was the critical-path dependency. It unblocked:
  - ORCH-005 (steering notes) -- inject user guidance between windows
  - ORCH-006 (capacity throttle) -- queue/resume policy
  - API-003 (orchestration control endpoints)
  - COORD-001 (merge coordinator queue model)
- ADPT-004 ensured all adapters speak the same language going forward
- DATA-004 enabled long conversations to resume from checkpoints rather than replaying full history

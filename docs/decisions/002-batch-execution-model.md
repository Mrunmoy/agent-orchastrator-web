# ADR-002: Batch Execution Model

## Status: Accepted

## Context

Agents in this system are CLI tools (Claude, Codex, Ollama) that run as subprocesses. Unbounded execution is dangerous: an agent could loop indefinitely, burn tokens, or produce divergent output without user oversight. We need a bounded execution model that gives users control between execution windows.

## Decision

We chose a **20-turn batch execution model** with pause/continue/stop controls, implemented in `BatchRunner` (`backend/src/agent_orchestrator/orchestrator/batch_runner.py`).

Key design points:

- **Fixed batch size (default 20)**: Each `BatchRunner` instance is configured with a `batch_size` (default 20). The `run()` method loops from turn 1 to `batch_size`, calling one agent per turn via the round-robin scheduler.
- **Turn recording**: Every turn produces a `TurnRecord` dataclass capturing `turn_number`, `agent_id`, `prompt`, `response_text`, `status` (from `AdapterStatus`), and an ISO-8601 `timestamp`. These are accumulated in `_turn_log` and returned as part of the `BatchResult`.
- **Pause/stop signaling**: Two boolean flags (`_pause_requested`, `_stop_requested`) are checked between turns, not mid-turn. This means:
  - `pause()` sets `_pause_requested = True`. At the next turn boundary, the runner sets status to `RunStatus.PAUSED` and breaks.
  - `stop()` sets `_stop_requested = True`. At the next turn boundary, the runner sets status to `RunStatus.DONE` and breaks.
  - These can be called from another coroutine/thread while the batch is running.
- **Error isolation**: Adapter errors do not crash the batch. The `try/except Exception` block around the adapter call catches any error and records a `TurnRecord` with `AdapterStatus.ERROR` and empty `response_text`. The agent is reset to `IDLE` in a `finally` block regardless of outcome.
- **Status transitions**: The runner starts as `QUEUED`, moves to `RUNNING` at the top of `run()`, and ends as either `DONE` (all turns completed or stop requested), `PAUSED` (pause requested), or `WAITING_RESOURCES` (no agent available from scheduler).
- **BatchResult**: The `run()` method returns a `BatchResult` with `conversation_id`, `turns_completed`, `status`, and the full `turn_log`.

## Consequences

- **User steering between batches**: The 20-turn boundary creates natural checkpoints where users can review output, inject steering notes, adjust agent configuration, or stop the run. This supports the "engineering cockpit" UX goal.
- **Resilience**: A single adapter failure (timeout, crash, bad output) does not abort the entire batch. The error is logged and the next agent gets its turn.
- **No mid-turn interruption**: Pause and stop only take effect between turns. If an adapter call takes a long time (up to the 120s timeout), the user must wait for it to complete before the signal is honored. This is a deliberate simplicity tradeoff.
- **Memory accumulation**: The turn log grows linearly with batch size. For 20 turns this is negligible. If batch sizes were ever increased significantly, streaming or chunked logging would be needed.
- **Continuation**: After a `PAUSED` batch, a new `BatchRunner` can be created with the same scheduler state to continue from where the previous run left off.

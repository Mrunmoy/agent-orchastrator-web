# ADR-006: Capacity Throttle and Run Queuing

## Status: Accepted

## Context

CLI agents run as local subprocesses that consume CPU, memory, and potentially GPU resources. Running too many agents simultaneously can degrade the host machine, cause timeouts, or crash processes. We need a mechanism to limit concurrent execution based on system capacity.

## Decision

We implemented a threshold-based capacity throttle with a FIFO run queue (`backend/src/agent_orchestrator/orchestrator/throttle.py`).

### CapacityThrottle

The `CapacityThrottle` class tracks active runs and evaluates whether a new run is allowed based on three thresholds defined in `ThrottlePolicy`:

- `max_concurrent_runs` (default 3): Hard cap on simultaneous batch runs.
- `max_cpu_percent` (default 85.0%): CPU usage ceiling.
- `max_memory_percent` (default 90.0%): Memory usage ceiling.

The `check(cpu_percent, memory_percent)` method evaluates these thresholds in order (concurrent runs first, then CPU, then memory) and returns a `ThrottleDecision` containing:
- `allowed: bool` -- Whether the new run may start.
- `reason: str` -- Human-readable explanation if denied (empty string if allowed).
- `current_runs`, `cpu_percent`, `memory_percent` -- Current metrics for observability.

Active runs are tracked by conversation ID using an `OrderedDict` (used as an ordered set for deterministic iteration). `register_run()` and `release_run()` manage the tracking.

### RunQueue

The `RunQueue` class provides a FIFO queue for conversation runs that are denied by the throttle:

- `enqueue(conversation_id)` -- Add to the back of the queue. Idempotent: returns existing position if already queued.
- `dequeue()` -- Pop from the front.
- `position(conversation_id)` -- Return 0-indexed position or `None`.
- `pending()` -- Return all queued IDs in order.
- `remove(conversation_id)` -- Cancel a queued run.

The queue holds a reference to the `CapacityThrottle` for future integration where dequeue could automatically check capacity before releasing a run.

### Interaction with the batch runner

When a new batch run is requested:
1. The throttle's `check()` is called with current CPU and memory metrics (from the OPS-003 capacity telemetry).
2. If `allowed`, the run is registered via `register_run()` and the `BatchRunner` starts.
3. If denied, the conversation is placed in the `RunQueue` and the user is notified of the queue position.
4. When a running batch completes, `release_run()` frees the slot, and the next queued conversation can be dequeued and started.

## Consequences

- **Host protection**: The throttle prevents resource exhaustion on the local machine, which is critical for a local-first tool that shares resources with the user's other work.
- **Configurable policy**: `ThrottlePolicy` is a frozen dataclass with sensible defaults. Users or operators can adjust thresholds based on their hardware.
- **Predictable ordering**: FIFO queuing ensures fairness -- the longest-waiting conversation runs next. No priority-based queue jumping.
- **No preemption**: Running batches are never interrupted to free capacity. The throttle only gates new starts. If a running batch is consuming too many resources, the user must manually pause or stop it.
- **External metrics required**: The throttle does not collect CPU/memory metrics itself. The caller must supply current values (from `backend/src/agent_orchestrator/runtime/capacity.py` or similar). This keeps the throttle pure and testable.
- **Single-machine assumption**: The throttle tracks runs in-process. It does not coordinate across multiple orchestrator instances. This is acceptable for the local-first architecture.

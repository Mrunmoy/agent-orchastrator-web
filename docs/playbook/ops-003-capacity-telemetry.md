# Playbook Entry: OPS-003 Capacity Telemetry Snapshot

## Date
2026-03-07

## Context
- Area/module: `backend/src/agent_orchestrator/runtime/capacity.py`
- Trigger: The scheduler needs machine resource data to auto-throttle agent runs before launching new ones.

## Symptoms
- Without capacity gates, the orchestrator could launch unlimited concurrent agent runs, potentially exhausting CPU/RAM on the host machine.

## Root Cause
- No capacity-awareness existed in the runtime module. The scheduler had no way to query current machine load.

## Resolution
- Added `CapacitySnapshot` dataclass mirroring the `resource_snapshot` DB table fields.
- Added `capture_snapshot()` that reads 1-min CPU load average (as percent of total cores) and RAM usage via `psutil`.
- Added `CapacityVerdict` dataclass (`allowed`, `reason`).
- Added `check_capacity()` that evaluates three ordered gates:
  1. CPU load percent < 85% (configurable)
  2. Free RAM > 2048 MB (configurable)
  3. Active runs < max active runs
- Default thresholds exposed as module-level constants `CPU_MAX_PERCENT` and `RAM_MIN_FREE_MB`.

## Verification
- 22 new tests in `backend/tests/test_capacity.py` covering:
  - Dataclass field access and immutability
  - `capture_snapshot()` with mocked psutil
  - Each gate: denied above threshold, denied at exact threshold, allowed below threshold
  - Custom thresholds
  - Gate priority ordering (CPU checked first)
- All 89 backend tests pass. Ruff + black clean.

## Preventive Actions
- Future tasks (scheduler integration) should call `check_capacity()` before launching runs.
- GPU telemetry is stubbed as `"[]"` -- a follow-up task can enumerate GPUs when needed.

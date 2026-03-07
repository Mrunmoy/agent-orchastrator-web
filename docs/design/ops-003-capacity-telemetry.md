# Feature Design: OPS-003 Capacity Telemetry Snapshot

## Context
- Problem: The scheduler needs real-time machine resource data to auto-throttle agent runs. Without capacity awareness, the system could overload the host by launching too many concurrent agents.
- Scope: Pure-Python module that reads CPU load and RAM usage via `psutil`, packages them into a dataclass, and evaluates capacity gates. No persistence, no scheduling logic.
- Non-goals: Database writes, GPU enumeration (stubbed as `[]`), scheduler integration, HTTP endpoints.

## Requirements
- Functional:
  - `CapacitySnapshot` dataclass mirroring `resource_snapshot` table fields.
  - `capture_snapshot()` reads 1-min CPU load average and RAM via `psutil`, returns `CapacitySnapshot`.
  - `check_capacity()` evaluates a snapshot against thresholds, returns `CapacityVerdict` with `allowed: bool` and `reason: str | None`.
  - Default threshold constants: `CPU_MAX_PERCENT = 85.0`, `RAM_MIN_FREE_MB = 2048`.
- Non-functional:
  - No I/O beyond `psutil` reads; function is synchronous and fast.
  - All `psutil` calls mockable in tests.

## Proposed Design
- Components/modules involved: `backend/src/agent_orchestrator/runtime/capacity.py`
- Data model changes: None (dataclasses only, no DB writes).
- API changes: None.
- UI changes: None.

### Module structure

```
runtime/
  __init__.py          # existing docstring
  capacity.py          # NEW - CapacitySnapshot, CapacityVerdict, capture_snapshot, check_capacity
```

### Key types

- `CapacitySnapshot`: frozen dataclass with `cpu_load_1m`, `ram_used_mb`, `ram_total_mb`, `gpu_json`, `agent_capacity_available`, `captured_at`.
- `CapacityVerdict`: frozen dataclass with `allowed: bool`, `reason: str | None`.
- `capture_snapshot(agent_capacity_available: int = 0) -> CapacitySnapshot`
- `check_capacity(snapshot, *, cpu_max_percent, ram_min_free_mb, max_active_runs, active_runs) -> CapacityVerdict`

## Alternatives Considered
1. Async psutil reads -- unnecessary overhead for simple stat reads.
2. Named tuple instead of dataclass -- dataclass is more idiomatic and supports defaults.

## Risks and Mitigations
- Risk: `psutil` unavailable in some environments.
- Mitigation: `psutil` is provided by the nix dev shell; import error will surface at startup.

## Test Strategy
- Unit: Mock `psutil.getloadavg` and `psutil.virtual_memory` to test both allowed and denied verdicts for each threshold (CPU, RAM, active runs), plus edge cases at exact thresholds.
- Integration: Deferred to OPS pipeline tasks.
- End-to-end: N/A for this slice.

## Acceptance Criteria
- [x] `CapacitySnapshot` dataclass exists with all `resource_snapshot` fields.
- [x] `capture_snapshot()` returns correct values from mocked psutil.
- [x] `check_capacity()` denies when CPU >= 85%.
- [x] `check_capacity()` denies when free RAM < 2048 MB.
- [x] `check_capacity()` denies when active_runs >= max_active_runs.
- [x] `check_capacity()` allows when all gates pass.
- [x] Edge cases at exact thresholds tested.
- [x] All backend tests pass; ruff + black clean.

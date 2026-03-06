# Background Scheduler Spec

## Purpose
Run multiple conversations in background with auto-throttled capacity control.

## User Outcomes
- Keep working across topics without losing progress.
- Get notified when blocked items need action.

## UI Spec
- History rows display execution status badges.
- Resource-unavailable message when start is denied.

## State Model
- `scheduler.capacity`
- `scheduler.running[]`
- `scheduler.queued[]`
- `scheduler.waitingForResources[]`

## Business Rules
- Auto-throttle by machine metrics + agent availability.
- If capacity unavailable: do not start, inform user, add resource-ready notification.

## API Contracts
- `GET /scheduler/status`
- `POST /scheduler/recheck`

## Persistence
- scheduler queue snapshot in `data/app_state.json`.

## Failure/Edge Cases
- Flapping capacity signals: apply debounce window.

## Test Cases
- Start denial when capacity full.
- Automatic readiness notification when capacity frees.

## Acceptance Criteria
- Scheduler never over-commits beyond configured safety thresholds.

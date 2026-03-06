# Top Bar Spec

## Purpose
Provide global context and primary run controls for the active conversation.

## User Outcomes
- See workspace, phase, gate, and run status instantly.
- Start or stop autonomous execution batches.

## UI Spec
- Elements: app title, `Phase` chip, `Gate` chip, `Working Directory` selector, status badge, `Run New Batch (N)`, `Stop Current Run`.
- Desktop layout: single horizontal bar.
- Mobile layout: wrapped rows, controls remain visible.

## State Model
- `activeConversationId`
- `phase`
- `gateStatus`
- `workdir`
- `runStatus` (`idle|running|paused|queued|failed`)
- `batchSize`

## Business Rules
- `Run New Batch` enabled only when conversation is `idle|paused` and scheduler allows start.
- `Stop Current Run` enabled only when conversation is `running`.

## API Contracts
- `GET /state`
- `POST /chat`
- `POST /stop`
- `POST /settings`

## Persistence
- `workdir`, `batchSize` in `data/app_state.json`.

## Failure/Edge Cases
- Invalid workdir: reject with message.
- Resource unavailable: show `not possible now` and queue notification.

## Test Cases
- Button enable/disable by status.
- Workdir switch persists across reload.
- Start blocked when scheduler says no capacity.

## Acceptance Criteria
- Top bar always reflects active conversation state within one polling cycle.

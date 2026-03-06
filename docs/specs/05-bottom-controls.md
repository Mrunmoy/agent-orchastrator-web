# Bottom Controls Spec

## Purpose
Capture user steering and phase-control actions between batches.

## User Outcomes
- Provide direction and preferences.
- Continue paused runs safely.
- Trigger gate review.

## UI Spec
- Inputs: `Steering Note`, `Preference Note`.
- Buttons: `Continue Batch (N) With Notes`, `Mark Gate Ready For My Review`.

## State Model
- `pendingSteeringNote`
- `pendingPreferenceNote`
- `batchSize`

## Business Rules
- Continue button enabled only in `paused` state.
- Notes injected as high-priority prompt prefix on next turn.

## API Contracts
- `POST /steer`
- `POST /continue`
- `POST /gate/approve` (for user review flow)

## Persistence
- latest notes in conversation state snapshot/checkpoint.

## Failure/Edge Cases
- Empty notes allowed; continue still valid.

## Test Cases
- Continue with notes updates next agent prompt context.

## Acceptance Criteria
- User steering directly affects subsequent agent behavior.

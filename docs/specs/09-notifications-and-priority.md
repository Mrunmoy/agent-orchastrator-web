# Notifications and Priority Spec

## Purpose
Help user focus on conversations that need attention first.

## User Outcomes
- See urgent items at a glance.
- Distinguish info vs action-needed states.

## UI Spec
- Status icons/tags on conversation rows.
- Priority-driven ordering in history list.

## Priority Order
1. `Needs User Input`
2. `Failed/Error`
3. `Completed`
4. `In Progress`
5. `Queued/Saved`

## State Model
- `notifications[]` per conversation
- `unreadCount` optional

## Business Rules
- Resource-free notifications appear when queued runs can start.
- Acknowledging notification does not clear conversation status unless state changes.

## API Contracts
- `POST /conversations/notify-ack`
- `GET /events`

## Persistence
- notification state in conversation metadata.

## Failure/Edge Cases
- duplicate event emission -> deduplicate by notification id/hash.

## Test Cases
- Priority sorting correctness.
- Status badge updates when state transitions.

## Acceptance Criteria
- Highest priority conversation is always visually obvious.

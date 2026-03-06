# API Schema Spec

## Purpose
Define stable contracts between frontend, orchestrator, and adapters.

## Endpoints
- `GET /state`
- `GET /events?since=&conversation_id=`
- `GET /conversations`
- `POST /conversations/new`
- `POST /conversations/select`
- `POST /conversations/delete`
- `POST /conversations/clear-all`
- `POST /chat`
- `POST /continue`
- `POST /steer`
- `POST /stop`
- `POST /phase`
- `POST /gate/approve`
- `POST /agents`
- `POST /settings`
- `GET /personalities`
- `GET /scheduler/status`
- `POST /scheduler/recheck`
- `POST /moderate`
- `POST /summarize`
- `POST /gate-check`

## Contract Rules
- All responses include `ok` and `error` envelope.
- Mutating endpoints require `conversation_id` when applicable.
- Event payloads include monotonically increasing `event_id`.

## Validation
- JSON Schema per request/response under `docs/specs/schema/` (to be added).

## Acceptance Criteria
- API contracts are sufficient for independent frontend/backend implementation.

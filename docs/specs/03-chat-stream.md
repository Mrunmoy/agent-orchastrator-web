# Chat Stream Spec

## Purpose
Present a linear, Slack-like message stream for the selected conversation.

## User Outcomes
- Read who said what and when.
- Understand current context without thread complexity.

## UI Spec
- Message row: avatar, bold speaker name, timestamp, message text.
- Day/batch separators.
- Typing indicator for active agent.
- Composer fixed at bottom of stream.

## State Model
- `messages[]` ordered by id/time
- `typingAgent`
- `targetAgentId`
- `composerText`

## Business Rules
- No thread model.
- Message order is append-only per conversation timeline.
- Incoming events update stream incrementally (`since_id` polling).

## API Contracts
- `GET /events?since=<id>&conversation_id=<id>`
- `POST /chat`

## Persistence
- `data/transcripts/<conversation_id>.jsonl`

## Failure/Edge Cases
- Poll gaps/reconnect: request from last known id.
- Large transcript: virtualized rendering recommended.

## Test Cases
- Proper rendering for user/agent/system/error messages.
- Typing indicator appears/disappears correctly.

## Acceptance Criteria
- Chat stream remains readable and accurate under continuous updates.

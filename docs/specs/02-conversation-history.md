# Conversation History Spec

## Purpose
Manage multiple long-lived conversations with fast switching and status awareness.

## User Outcomes
- Browse many conversations in a scrollable list.
- Create, delete, clear all conversations.
- Identify high-priority conversations quickly.

## UI Spec
- Left pane sections: actions row, `Recent` scrollable list, `Agents In This Conversation`.
- Row contents: title, last update, status tag/icon, metadata.
- Status priority render order:
1. `Needs User Input`
2. `Failed/Error`
3. `Completed`
4. `In Progress`
5. `Queued/Saved`

## State Model
- `conversations[]` metadata list
- `activeConversationId`
- `notificationState` per conversation

## Business Rules
- Selecting a conversation does not stop other running conversations.
- Delete one conversation removes from active list and archives/soft-deletes data.
- Clear all requires explicit confirmation.

## API Contracts
- `GET /conversations`
- `POST /conversations/new`
- `POST /conversations/select`
- `POST /conversations/delete`
- `POST /conversations/clear-all`

## Persistence
- `data/conversations.json` for metadata and status.

## Failure/Edge Cases
- Selecting deleted conversation -> not found handling.
- Clearing while some conversations running -> require stop or force policy.

## Test Cases
- Scroll behavior with 100+ conversations.
- Active row updates correctly.
- Delete/clear actions update storage and UI.

## Acceptance Criteria
- History pane remains usable and responsive with large conversation counts.

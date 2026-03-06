# Intelligence Pane Spec

## Purpose
Show post-batch decision intelligence: agreements, conflicts, neutral memo.

## User Outcomes
- Quickly see where agents agree/disagree.
- Use neutral memo to steer next batch.

## UI Spec
- Cards:
1. `Agreement Map`
2. `Conflict Map` table
3. `Ollama Neutral Memo`
- Action: `Apply Memo As Steering`.

## State Model
- `latestBatchArtifact`
- `artifactHistory[]` optional

## Business Rules
- Update pane when batch finishes.
- If no artifact available, show placeholder state.

## API Contracts
- `GET /events`
- `POST /moderate`
- `POST /summarize`
- `POST /gate-check`

## Persistence
- `data/artifacts/<conversation_id>/<batch_id>.json`

## Failure/Edge Cases
- Ollama unavailable: show degraded status and keep worker outputs visible.

## Test Cases
- Artifact schema validation.
- `Apply Memo` fills steering fields correctly.

## Acceptance Criteria
- User can make next-step decisions from pane without re-reading full chat.

# Persistence and Resume Spec

## Purpose
Guarantee reliable conversation continuity with low token cost.

## User Outcomes
- Resume any conversation accurately.
- Avoid expensive full transcript replay.

## UI Spec
- History row selection triggers resume load state.
- Optional info hint: resume source/size.

## State Model
- `conversationMetadata`
- `checkpoint`
- `resumePack`

## Business Rules
- Checkpoint-first resume model.
- Provider session IDs are optional optimizations only.
- Dual modes:
1. `continue-session` (if valid provider session exists)
2. `reconstruct` (fresh run with checkpoint pack)

## Resume Pack Contents
1. objective + constraints
2. phase + gate state
3. latest steering/preference
4. last 2 summaries
5. latest agreement/conflict/memo artifact
6. last 8-12 messages

## Token Budget
- soft: 1200-2800 tokens
- hard cap: 3500 default
- truncation order: reduce recent window first, keep decisions/conflicts mandatory

## API Contracts
- `POST /conversations/select`

## Persistence
- `data/conversations.json`
- `data/transcripts/*.jsonl`
- `data/summaries/*.json`
- `data/artifacts/*`
- `data/checkpoints/*.json`

## Failure/Edge Cases
- missing/expired session id -> fallback to `reconstruct`.

## Test Cases
- Resume correctness with and without provider session IDs.
- Hard-cap truncation behavior deterministic.

## Acceptance Criteria
- Conversation resume remains accurate and token-bounded.

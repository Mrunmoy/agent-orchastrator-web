# Test Plan Spec

## Purpose
Ensure the platform is reliable under multi-conversation autonomous workloads.

## Test Layers
1. Unit tests
- scheduler decisions
- phase/gate transitions
- resume pack builder and token cap truncation
- status priority sorting

2. API tests
- conversation CRUD
- start/continue/stop
- notification ack
- scheduler status and recheck

3. Integration tests
- background execution while user switches conversations
- worker/coordinator merge pipeline behavior
- clarification branch pause with unrelated branch continuation

4. UI tests
- history list scroll/perf
- status badge rendering and updates
- message stream rendering

5. End-to-end scenario
- debate -> agreement -> go-ahead -> task split -> autonomous work -> integration -> notify user -> sign-off

## Quality Gates
- No regression on core orchestration loop.
- Resume works with and without provider session IDs.
- No concurrent direct-main merge attempts.

## Acceptance Criteria
- All required conversation lifecycle flows are covered by automated tests.

# Permissions and Merge Coordinator Spec

## Purpose
Prevent merge-conflict loops while allowing broad autonomous execution.

## User Outcomes
- Agents can build/test autonomously.
- Integration and merge remain controlled and traceable.

## UI Spec
- Permission profile selection before autonomous run.
- Coordinator role visible in conversation agent list.

## State Model
- `permissionProfile`
- `mergeCoordinatorAgentId`
- `mergeState`

## Business Rules
- Workers: code/test/docs on isolated branches/worktrees.
- Single coordinator: integration + merge candidate preparation.
- Main merge always user-gated.

## API Contracts
- `POST /agents`
- `POST /settings` (permission profile)
- `POST /gate/approve`

## Persistence
- role and permission profile in conversation metadata.

## Failure/Edge Cases
- Coordinator unavailable: reassign policy or pause integration.

## Test Cases
- Two workers cannot merge main simultaneously.
- Coordinator-only integration path enforced.

## Acceptance Criteria
- Serialized merge pipeline guaranteed under concurrent workloads.

# Parallel Agent Workflow

## Goal
Enable multiple CLI agents to implement independent parts in parallel while keeping integration safe and predictable.

## Model
- `N` worker agents implement scoped tasks on separate branches/worktrees.
- `1` merge coordinator agent performs sequential integration.
- User remains approval gate for risky/destructive actions.

## Setup
1. Initialize worktrees:
   ```bash
   make parallel-init AGENTS="codex-ui claude-orchestrator ollama-data"
   ```
   Optional namespace override:
   ```bash
   BRANCH_PREFIX=codex ./scripts/parallel_init.sh ui chat storage
   ```
2. Preferred: create worktree by task ID:
   ```bash
   make task-worktree TASK_ID=UI-001 PREFIX=claude
   ```
   This reads task metadata from `config/tasks.json` and creates the right branch/worktree.
3. Assign one task per agent in `docs/coordination/task-board.md`.
4. Launch each agent CLI in its own worktree path.

## Branching Rules
- Branch naming: `agent/<agent-name>`
- No direct commits to `master` except by merge coordinator.
- Rebase onto `master` before requesting integration.

## Integration Rules
1. Worker marks task as `Review` with test evidence.
2. Merge coordinator validates in clean tree:
   - `nix develop`
   - `make test-ui` (and backend tests once added)
3. Merge queue is processed one branch at a time.
4. On conflict, branch is bounced back to owner.

## Conflict Avoidance
- Assign vertical slices when possible (UI vs scheduler vs storage).
- Avoid two agents editing same file in same cycle.
- For shared interfaces, merge interface changes first, then dependents.

## Runtime Throttling
- Scheduler checks host capacity and agent availability before starting new cycle.
- If capacity is low, conversation moves to `Queued` and user is notified.
- Resume automatically when thresholds recover.

## Recommended Capacity Gates (Initial)
- CPU usage < 85%
- RAM free > 2.0 GiB
- Active agent runs <= configured max parallel runs

## Definition of Done per Task
- Design notes updated (if behavior changed).
- Tests added/updated and passing.
- Implementation committed in small slices.
- Task board status moved to `Done`.

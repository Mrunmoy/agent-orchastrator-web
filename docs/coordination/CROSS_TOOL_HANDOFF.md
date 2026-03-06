# Cross-Tool Handoff Protocol

## Purpose
Allow `codex-code` and `claude-code` to work in parallel, each managing multiple sub-agents, without stepping on each other.

## Topology
- User: final approval + steering.
- Manager agents: `codex-code`, `claude-code`.
- Sub-agents: worker agents spawned by each manager.
- Merge coordinator: single integration authority.

## Isolation Rules
- Each manager uses its own branch namespace:
  - Codex namespace: `codex/<worker>`
  - Claude namespace: `claude/<worker>`
- Prefer separate worktrees per worker.
- No direct merge to `master` by workers.

## Task Ownership
- Source of truth: `docs/coordination/task-board.md`.
- A task is exclusive once owner is set.
- Cross-cutting tasks must be split into sub-tasks before assignment.

## Delivery Contract Per Worker
- Code changes limited to assigned scope.
- Unit/integration tests updated and passing.
- Short verification memo in commit or PR description.
- Status moved to `Review` with branch name.

## Merge Coordinator Flow
1. Pull queued `Review` tasks.
2. Rebase branch on latest `master`.
3. Run validation checks.
4. Merge one branch at a time.
5. Update merge queue and task status.

## Conflict Policy
- If conflict occurs, bounce branch to original owner with conflict report.
- Do not force-push conflict resolutions from coordinator unless owner delegated explicitly.

## Steering and Batch Control
- Conversation executes in 20-turn batches by default.
- User can inject steering notes between batches.
- Managers must propagate steering updates to all active workers.

## Handoff Command
Generate manager-specific kickoff docs:
```bash
make handoff-packs
```


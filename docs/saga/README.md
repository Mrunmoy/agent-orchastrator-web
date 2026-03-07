# Project Saga Log

This directory contains the incremental milestone log for the **agent-orchestrator-web** project -- a multi-agent orchestration web application for running local CLI agents (Claude, Codex, Ollama) in structured debate-style conversations.

## What This Log Captures

Each milestone document records:

- **What was built** -- the tasks completed, files created, and capabilities added.
- **How it was built** -- the parallel worktree workflow, PR review cycle, and TDD discipline.
- **Key decisions** -- architectural choices and review findings that shaped the codebase.
- **Test coverage** -- how many tests were added at each stage.
- **What was unblocked** -- how each milestone enabled the next phase of work.

## Project Development Model

The project was developed using a parallel multi-agent workflow:

- **Nix dev shell** provides a reproducible environment for all agents.
- **Git worktrees** allow up to 5 tasks to run simultaneously in isolated directories.
- **TDD is mandatory** -- tests are written first (red phase), then implementation follows.
- **All work flows through PRs** to `main` with CI checks (GitHub Actions).
- **A merge coordinator** serializes integration to avoid conflicts.

Development proceeded in 4 parallel batches, each with 5 tasks running concurrently.

## Milestone Index

| # | Title | Tasks | Document |
|---|-------|-------|----------|
| 01 | Foundations | SETUP-001, SETUP-002, SETUP-003 | [milestone-01-foundations.md](milestone-01-foundations.md) |
| 02 | Core Infrastructure | DATA-001/002/003, ADPT-001/002/003, API-001/002, ORCH-001, OPS-003, UI-001 | [milestone-02-core-infrastructure.md](milestone-02-core-infrastructure.md) |
| 03 | Orchestration Engine (Batch 1) | ORCH-002/003, API-004/005, UI-002 | [milestone-03-orchestration-engine.md](milestone-03-orchestration-engine.md) |
| 04 | Execution Runtime (Batch 2) | ORCH-004, DATA-004, ADPT-004, UI-003, UI-005 | [milestone-04-execution-runtime.md](milestone-04-execution-runtime.md) |
| 05 | Coordination Layer (Batch 3) | ORCH-005/006, API-003, UI-006, COORD-001 | [milestone-05-coordination-layer.md](milestone-05-coordination-layer.md) |
| 06 | Production Readiness (Batch 4) | UI-004, COORD-002/003, OPS-001, TEST-002 | [milestone-06-production-readiness.md](milestone-06-production-readiness.md) |

## Narrative Chapters

The `*.html` files in this directory are storybook-style narrative chapters written during early development. They cover the same ground as milestones 01-02 but in a more narrative format.

## Relationship to Other Docs

- **Task board** (`docs/coordination/task-board.md`) -- real-time execution tracking.
- **TASKS.md** -- the source-of-truth backlog with completion checkboxes.
- **config/tasks.json** -- machine-readable task metadata.
- **Saga chapter template** -- `docs/templates/saga-chapter-template.md`.

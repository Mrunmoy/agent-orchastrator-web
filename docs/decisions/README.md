# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the agent-orchestrator-web project. Each ADR documents a significant technical decision, the context that led to it, and the consequences that follow.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-round-robin-scheduling.md) | Round-Robin Scheduling | Accepted |
| [002](002-batch-execution-model.md) | Batch Execution Model | Accepted |
| [003](003-checkpoint-resume-strategy.md) | Checkpoint-First Resume Strategy | Accepted |
| [004](004-adapter-pattern.md) | Adapter Pattern for CLI Agents | Accepted |
| [005](005-state-machine-transitions.md) | Conversation State Machine Transitions | Accepted |
| [006](006-capacity-throttle-and-queuing.md) | Capacity Throttle and Run Queuing | Accepted |
| [007](007-merge-serialization.md) | Merge Serialization and Lock Policy | Accepted |

## Format

Each ADR follows this structure:

```
# ADR-NNN: Title
## Status: Accepted | Deprecated | Superseded
## Context: What problem or question prompted this decision
## Decision: What we chose and how it works
## Consequences: Tradeoffs, implications, and what follows
```

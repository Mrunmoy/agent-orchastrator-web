# ADR-001: Round-Robin Scheduling

## Status: Accepted

## Context

The orchestrator needs to allocate turns among multiple CLI agents (Claude, Codex, Ollama) within a conversation. We considered three scheduling strategies:

1. **Priority-based** -- agents with higher priority get more turns. This introduces starvation risk and requires complex priority tuning per conversation.
2. **Random** -- agents are selected randomly each turn. This provides no fairness guarantees and makes conversation flow unpredictable for the user.
3. **Round-robin** -- agents cycle in a fixed order, each getting an equal share of turns. Simple, fair, and deterministic.

## Decision

We chose round-robin scheduling, implemented in `RoundRobinScheduler` (`backend/src/agent_orchestrator/orchestrator/scheduler.py`).

Key design points:

- **IDLE-only availability**: Only agents with `AgentStatus.IDLE` are eligible for selection. Agents that are `RUNNING`, `BLOCKED`, or `OFFLINE` are skipped. The eligible set is defined as `_AVAILABLE_STATUSES = frozenset({AgentStatus.IDLE})`.
- **Wrap-around with skip**: `next_agent()` iterates through the roster up to `n` times (roster size), advancing the internal index modulo `n`. If it completes a full cycle without finding an IDLE agent, it returns `None`.
- **Stateful index**: The scheduler maintains a `_index` position that persists across calls, ensuring the next call resumes from where the last left off rather than restarting from agent 0.
- **Interaction with the batch runner**: The `BatchRunner` calls `scheduler.next_agent()` at the top of each turn. Before calling the adapter, it marks the agent `RUNNING` via `mark_agent_status()`. After the adapter call (whether success or error), it resets the agent to `IDLE` in a `finally` block.
- **No persistence**: The scheduler is pure in-memory logic with no async, no DB. It is instantiated per batch run with a roster of `Agent` dataclasses.

## Consequences

- **Fair turn distribution**: Every IDLE agent gets an equal number of turns over time, which aligns with the debate-to-agreement workflow where each agent's perspective matters equally.
- **Simple mental model**: Users and developers can predict which agent speaks next by looking at the roster order.
- **Graceful degradation**: If agents go offline or become blocked, the scheduler skips them without crashing. If all agents are unavailable, `next_agent()` returns `None` and the batch runner sets status to `WAITING_RESOURCES`.
- **No priority support**: If a future workflow needs weighted turn allocation, the scheduler would need to be extended or replaced. For now, equal turns are sufficient.
- **Reset capability**: `reset()` sets the index back to 0, useful when a batch is restarted or the roster changes.

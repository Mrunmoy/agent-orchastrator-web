"""Round-robin scheduler for agent turn management (ORCH-003).

Pure logic — no async, no DB. Cycles through a roster of agents in order,
skipping BLOCKED and OFFLINE agents.
"""

from __future__ import annotations

from agent_orchestrator.orchestrator.models import Agent, AgentStatus


class RoundRobinScheduler:
    """Cycle through agents in round-robin order, skipping unavailable ones."""

    _AVAILABLE_STATUSES = frozenset({AgentStatus.IDLE, AgentStatus.RUNNING})

    def __init__(self, roster: list[Agent]) -> None:
        self._roster = list(roster)
        self._index = 0

    # ── Public API ──────────────────────────────────────────────────────

    def next_agent(self) -> Agent | None:
        """Return the next available agent, or *None* if none are available."""
        n = len(self._roster)
        if n == 0:
            return None

        for _ in range(n):
            agent = self._roster[self._index]
            self._index = (self._index + 1) % n
            if agent.status in self._AVAILABLE_STATUSES:
                return agent

        return None

    def reset(self) -> None:
        """Reset the rotation index to 0."""
        self._index = 0

    @property
    def current_index(self) -> int:
        """Current position in the rotation."""
        return self._index

    @property
    def available_agents(self) -> list[Agent]:
        """Agents whose status is IDLE or RUNNING."""
        return [a for a in self._roster if a.status in self._AVAILABLE_STATUSES]

    def mark_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update an agent's status in the roster. No-op if *agent_id* not found."""
        for agent in self._roster:
            if agent.id == agent_id:
                agent.status = status
                return

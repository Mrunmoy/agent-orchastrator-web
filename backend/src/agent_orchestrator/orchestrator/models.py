"""Domain models for the orchestration core (ORCH-001).

Canonical data structures matching docs/specs/12-domain-model.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Provider(str, Enum):
    """CLI agent provider."""

    CODEX = "codex"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class AgentRole(str, Enum):
    """Role an agent plays within a conversation."""

    WORKER = "worker"
    COORDINATOR = "coordinator"
    MODERATOR = "moderator"


class AgentStatus(str, Enum):
    """Current operational status of an agent."""

    IDLE = "idle"
    RUNNING = "running"
    BLOCKED = "blocked"
    OFFLINE = "offline"


class ConversationState(str, Enum):
    """High-level state of a conversation."""

    DEBATE = "debate"
    EXECUTION_PLANNING = "execution_planning"
    AUTONOMOUS_WORK = "autonomous_work"
    NEEDS_USER_INPUT = "needs_user_input"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"


class Phase(str, Enum):
    """Workflow phase within a conversation."""

    DESIGN_DEBATE = "design_debate"
    TDD_PLANNING = "tdd_planning"
    IMPLEMENTATION = "implementation"
    INTEGRATION = "integration"
    DOCS = "docs"
    MERGE = "merge"


class GateStatus(str, Enum):
    """Approval status of a phase gate."""

    OPEN = "open"
    SATISFIED = "satisfied"
    APPROVED = "approved"


class TaskStatus(str, Enum):
    """Status of a task within a conversation."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    FAILED = "failed"


class RunStatus(str, Enum):
    """Status of a scheduler run."""

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_RESOURCES = "waiting_resources"
    DONE = "done"
    FAILED = "failed"


class ArtifactType(str, Enum):
    """Type of structured artifact produced during orchestration."""

    AGREEMENT_MAP = "agreement_map"
    CONFLICT_MAP = "conflict_map"
    NEUTRAL_MEMO = "neutral_memo"
    CHECKPOINT = "checkpoint"
    TEST_REPORT = "test_report"
    DECISION_LOG = "decision_log"


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------


@dataclass
class Agent:
    """A CLI agent instance."""

    id: str
    display_name: str
    provider: Provider
    model: str
    role: AgentRole
    status: AgentStatus
    capabilities_json: str
    created_at: str
    updated_at: str
    personality_key: str | None = None
    session_id: str | None = None


@dataclass
class Conversation:
    """A long-lived orchestration workspace."""

    id: str
    title: str
    project_path: str
    state: ConversationState
    phase: Phase
    gate_status: GateStatus
    created_at: str
    updated_at: str
    priority: int = 100
    active: int = 0
    summary_snapshot: str | None = None
    latest_artifact_id: str | None = None
    deleted_at: str | None = None


@dataclass
class ConversationAgent:
    """Join table: per-conversation agent configuration."""

    id: str
    conversation_id: str
    agent_id: str
    turn_order: int
    permission_profile: str
    created_at: str
    enabled: int = 1
    is_merge_coordinator: int = 0


@dataclass
class Task:
    """A work item scoped to a conversation."""

    id: str
    conversation_id: str
    title: str
    spec_json: str
    status: TaskStatus
    created_at: str
    updated_at: str
    priority: int = 100
    owner_agent_id: str | None = None
    depends_on_json: str = "[]"
    started_at: str | None = None
    finished_at: str | None = None
    result_summary: str | None = None
    evidence_json: str = "[]"


@dataclass
class Artifact:
    """A structured output produced during orchestration."""

    id: str
    conversation_id: str
    type: ArtifactType
    payload_json: str
    created_at: str
    batch_id: str | None = None


@dataclass
class MessageEvent:
    """A chat message or system event in the conversation stream."""

    conversation_id: str
    event_id: str
    source_type: str
    text: str
    event_type: str
    created_at: str
    id: int | None = None
    source_id: str | None = None
    metadata_json: str = field(default="{}")


@dataclass
class SchedulerRun:
    """A batch execution run managed by the scheduler."""

    id: str
    conversation_id: str
    status: RunStatus
    batch_size: int
    created_at: str
    reason: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


@dataclass
class ResourceSnapshot:
    """Machine resource telemetry for auto-throttle decisions."""

    captured_at: str
    cpu_load_1m: float
    ram_used_mb: int
    ram_total_mb: int
    agent_capacity_available: int
    id: int | None = None
    gpu_json: str = "[]"

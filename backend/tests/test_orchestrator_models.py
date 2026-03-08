"""Tests for orchestrator domain models (ORCH-001).

Written FIRST (TDD) — these must fail before implementation exists.
"""

from __future__ import annotations

import dataclasses

from agent_orchestrator.orchestrator.models import (
    Agent,
    AgentRole,
    AgentStatus,
    Artifact,
    ArtifactType,
    Conversation,
    ConversationAgent,
    ConversationState,
    GateStatus,
    MessageEvent,
    Phase,
    Provider,
    ResourceSnapshot,
    RunStatus,
    SchedulerRun,
    Task,
    TaskStatus,
)

# ---------------------------------------------------------------------------
# Enum completeness
# ---------------------------------------------------------------------------


class TestProviderEnum:
    def test_members(self):
        assert set(Provider) == {
            Provider.CODEX,
            Provider.CLAUDE,
            Provider.GEMINI,
            Provider.OLLAMA,
        }

    def test_values(self):
        assert Provider.CODEX.value == "codex"
        assert Provider.CLAUDE.value == "claude"
        assert Provider.GEMINI.value == "gemini"
        assert Provider.OLLAMA.value == "ollama"


class TestAgentRoleEnum:
    def test_members(self):
        assert set(AgentRole) == {
            AgentRole.WORKER,
            AgentRole.COORDINATOR,
            AgentRole.MODERATOR,
        }

    def test_values(self):
        assert AgentRole.WORKER.value == "worker"
        assert AgentRole.COORDINATOR.value == "coordinator"
        assert AgentRole.MODERATOR.value == "moderator"


class TestAgentStatusEnum:
    def test_members(self):
        assert set(AgentStatus) == {
            AgentStatus.IDLE,
            AgentStatus.RUNNING,
            AgentStatus.BLOCKED,
            AgentStatus.OFFLINE,
        }

    def test_values(self):
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.BLOCKED.value == "blocked"
        assert AgentStatus.OFFLINE.value == "offline"


class TestConversationStateEnum:
    def test_members(self):
        assert set(ConversationState) == {
            ConversationState.DEBATE,
            ConversationState.EXECUTION_PLANNING,
            ConversationState.AUTONOMOUS_WORK,
            ConversationState.NEEDS_USER_INPUT,
            ConversationState.COMPLETED,
            ConversationState.FAILED,
            ConversationState.QUEUED,
        }

    def test_values(self):
        assert ConversationState.DEBATE.value == "debate"
        assert ConversationState.EXECUTION_PLANNING.value == "execution_planning"
        assert ConversationState.AUTONOMOUS_WORK.value == "autonomous_work"
        assert ConversationState.NEEDS_USER_INPUT.value == "needs_user_input"
        assert ConversationState.COMPLETED.value == "completed"
        assert ConversationState.FAILED.value == "failed"
        assert ConversationState.QUEUED.value == "queued"


class TestPhaseEnum:
    def test_members(self):
        assert set(Phase) == {
            Phase.DESIGN_DEBATE,
            Phase.TDD_PLANNING,
            Phase.IMPLEMENTATION,
            Phase.INTEGRATION,
            Phase.DOCS,
            Phase.MERGE,
        }

    def test_values(self):
        assert Phase.DESIGN_DEBATE.value == "design_debate"
        assert Phase.TDD_PLANNING.value == "tdd_planning"
        assert Phase.IMPLEMENTATION.value == "implementation"
        assert Phase.INTEGRATION.value == "integration"
        assert Phase.DOCS.value == "docs"
        assert Phase.MERGE.value == "merge"


class TestGateStatusEnum:
    def test_members(self):
        assert set(GateStatus) == {
            GateStatus.OPEN,
            GateStatus.SATISFIED,
            GateStatus.APPROVED,
        }

    def test_values(self):
        assert GateStatus.OPEN.value == "open"
        assert GateStatus.SATISFIED.value == "satisfied"
        assert GateStatus.APPROVED.value == "approved"


class TestTaskStatusEnum:
    def test_members(self):
        assert set(TaskStatus) == {
            TaskStatus.TODO,
            TaskStatus.DESIGN,
            TaskStatus.TDD,
            TaskStatus.IMPLEMENTING,
            TaskStatus.TESTING,
            TaskStatus.PR_RAISED,
            TaskStatus.IN_REVIEW,
            TaskStatus.FIXING_COMMENTS,
            TaskStatus.MERGING,
            TaskStatus.DONE,
            TaskStatus.BLOCKED,
        }

    def test_values(self):
        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.DESIGN.value == "design"
        assert TaskStatus.TDD.value == "tdd"
        assert TaskStatus.IMPLEMENTING.value == "implementing"
        assert TaskStatus.TESTING.value == "testing"
        assert TaskStatus.PR_RAISED.value == "pr_raised"
        assert TaskStatus.IN_REVIEW.value == "in_review"
        assert TaskStatus.FIXING_COMMENTS.value == "fixing_comments"
        assert TaskStatus.MERGING.value == "merging"
        assert TaskStatus.DONE.value == "done"
        assert TaskStatus.BLOCKED.value == "blocked"


class TestRunStatusEnum:
    def test_members(self):
        assert set(RunStatus) == {
            RunStatus.QUEUED,
            RunStatus.RUNNING,
            RunStatus.PAUSED,
            RunStatus.WAITING_RESOURCES,
            RunStatus.DONE,
            RunStatus.FAILED,
        }

    def test_values(self):
        assert RunStatus.QUEUED.value == "queued"
        assert RunStatus.RUNNING.value == "running"
        assert RunStatus.PAUSED.value == "paused"
        assert RunStatus.WAITING_RESOURCES.value == "waiting_resources"
        assert RunStatus.DONE.value == "done"
        assert RunStatus.FAILED.value == "failed"


class TestArtifactTypeEnum:
    def test_members(self):
        assert set(ArtifactType) == {
            ArtifactType.AGREEMENT_MAP,
            ArtifactType.CONFLICT_MAP,
            ArtifactType.NEUTRAL_MEMO,
            ArtifactType.CHECKPOINT,
            ArtifactType.TEST_REPORT,
            ArtifactType.DECISION_LOG,
        }

    def test_values(self):
        assert ArtifactType.AGREEMENT_MAP.value == "agreement_map"
        assert ArtifactType.CONFLICT_MAP.value == "conflict_map"
        assert ArtifactType.NEUTRAL_MEMO.value == "neutral_memo"
        assert ArtifactType.CHECKPOINT.value == "checkpoint"
        assert ArtifactType.TEST_REPORT.value == "test_report"
        assert ArtifactType.DECISION_LOG.value == "decision_log"


# ---------------------------------------------------------------------------
# Dataclass instantiation
# ---------------------------------------------------------------------------

NOW = "2026-03-07T12:00:00Z"


class TestAgent:
    def test_instantiation(self):
        agent = Agent(
            id="a-1",
            display_name="Codex Reviewer",
            provider=Provider.CODEX,
            model="codex-mini",
            role=AgentRole.WORKER,
            status=AgentStatus.IDLE,
            capabilities_json="[]",
            created_at=NOW,
            updated_at=NOW,
        )
        assert agent.id == "a-1"
        assert agent.display_name == "Codex Reviewer"
        assert agent.provider == Provider.CODEX
        assert agent.model == "codex-mini"
        assert agent.role == AgentRole.WORKER
        assert agent.status == AgentStatus.IDLE

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(Agent)

    def test_optional_fields_default_none(self):
        agent = Agent(
            id="a-2",
            display_name="Test",
            provider=Provider.CLAUDE,
            model="opus",
            role=AgentRole.COORDINATOR,
            status=AgentStatus.IDLE,
            capabilities_json="{}",
            created_at=NOW,
            updated_at=NOW,
        )
        assert agent.personality_key is None
        assert agent.session_id is None


class TestConversation:
    def test_instantiation(self):
        conv = Conversation(
            id="c-1",
            title="Design debate",
            project_path="/tmp/proj",
            state=ConversationState.DEBATE,
            phase=Phase.DESIGN_DEBATE,
            gate_status=GateStatus.OPEN,
            created_at=NOW,
            updated_at=NOW,
        )
        assert conv.id == "c-1"
        assert conv.state == ConversationState.DEBATE
        assert conv.phase == Phase.DESIGN_DEBATE
        assert conv.gate_status == GateStatus.OPEN

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(Conversation)

    def test_defaults(self):
        conv = Conversation(
            id="c-2",
            title="T",
            project_path="/p",
            state=ConversationState.QUEUED,
            phase=Phase.DESIGN_DEBATE,
            gate_status=GateStatus.OPEN,
            created_at=NOW,
            updated_at=NOW,
        )
        assert conv.priority == 100
        assert conv.active == 0
        assert conv.summary_snapshot is None
        assert conv.latest_artifact_id is None
        assert conv.deleted_at is None


class TestConversationAgent:
    def test_instantiation(self):
        ca = ConversationAgent(
            id="ca-1",
            conversation_id="c-1",
            agent_id="a-1",
            turn_order=1,
            permission_profile="full",
            created_at=NOW,
        )
        assert ca.conversation_id == "c-1"
        assert ca.agent_id == "a-1"
        assert ca.turn_order == 1

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(ConversationAgent)

    def test_defaults(self):
        ca = ConversationAgent(
            id="ca-2",
            conversation_id="c-1",
            agent_id="a-1",
            turn_order=0,
            permission_profile="read",
            created_at=NOW,
        )
        assert ca.enabled == 1
        assert ca.is_merge_coordinator == 0


class TestTask:
    def test_instantiation(self):
        task = Task(
            id="t-1",
            conversation_id="c-1",
            title="Implement models",
            spec_json="{}",
            status=TaskStatus.TODO,
            created_at=NOW,
            updated_at=NOW,
        )
        assert task.id == "t-1"
        assert task.status == TaskStatus.TODO

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(Task)

    def test_defaults(self):
        task = Task(
            id="t-2",
            conversation_id="c-1",
            title="T",
            spec_json="{}",
            status=TaskStatus.TODO,
            created_at=NOW,
            updated_at=NOW,
        )
        assert task.priority == 100
        assert task.owner_agent_id is None
        assert task.depends_on_json == "[]"
        assert task.started_at is None
        assert task.finished_at is None
        assert task.result_summary is None
        assert task.evidence_json == "[]"


class TestArtifact:
    def test_instantiation(self):
        art = Artifact(
            id="art-1",
            conversation_id="c-1",
            type=ArtifactType.AGREEMENT_MAP,
            payload_json='{"agreed": true}',
            created_at=NOW,
        )
        assert art.type == ArtifactType.AGREEMENT_MAP
        assert art.payload_json == '{"agreed": true}'

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(Artifact)

    def test_optional_batch_id(self):
        art = Artifact(
            id="art-2",
            conversation_id="c-1",
            type=ArtifactType.CHECKPOINT,
            payload_json="{}",
            created_at=NOW,
        )
        assert art.batch_id is None


class TestMessageEvent:
    def test_instantiation(self):
        msg = MessageEvent(
            conversation_id="c-1",
            event_id="evt-1",
            source_type="agent",
            text="Hello world",
            event_type="message",
            created_at=NOW,
        )
        assert msg.conversation_id == "c-1"
        assert msg.event_id == "evt-1"
        assert msg.source_type == "agent"
        assert msg.text == "Hello world"

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(MessageEvent)

    def test_defaults(self):
        msg = MessageEvent(
            conversation_id="c-1",
            event_id="evt-2",
            source_type="system",
            text="ping",
            event_type="heartbeat",
            created_at=NOW,
        )
        assert msg.id is None
        assert msg.source_id is None
        assert msg.metadata_json == "{}"


class TestSchedulerRun:
    def test_instantiation(self):
        run = SchedulerRun(
            id="run-1",
            conversation_id="c-1",
            status=RunStatus.QUEUED,
            batch_size=20,
            created_at=NOW,
        )
        assert run.status == RunStatus.QUEUED
        assert run.batch_size == 20

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(SchedulerRun)

    def test_defaults(self):
        run = SchedulerRun(
            id="run-2",
            conversation_id="c-1",
            status=RunStatus.RUNNING,
            batch_size=10,
            created_at=NOW,
        )
        assert run.reason is None
        assert run.started_at is None
        assert run.ended_at is None


class TestResourceSnapshot:
    def test_instantiation(self):
        snap = ResourceSnapshot(
            captured_at=NOW,
            cpu_load_1m=42.5,
            ram_used_mb=4096,
            ram_total_mb=16384,
            agent_capacity_available=3,
        )
        assert snap.cpu_load_1m == 42.5
        assert snap.ram_used_mb == 4096
        assert snap.ram_total_mb == 16384

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(ResourceSnapshot)

    def test_defaults(self):
        snap = ResourceSnapshot(
            captured_at=NOW,
            cpu_load_1m=10.0,
            ram_used_mb=2048,
            ram_total_mb=8192,
            agent_capacity_available=5,
        )
        assert snap.id is None
        assert snap.gpu_json == "[]"


# ---------------------------------------------------------------------------
# Re-export from __init__
# ---------------------------------------------------------------------------


class TestReExport:
    def test_all_models_importable_from_orchestrator(self):
        from agent_orchestrator.orchestrator import (  # noqa: F401
            VALID_TRANSITIONS,
            Agent,
            AgentRole,
            AgentStatus,
            Artifact,
            ArtifactType,
            Conversation,
            ConversationAgent,
            ConversationState,
            EventType,
            GateStatus,
            MergeQueueStatus,
            MessageEvent,
            Phase,
            Provider,
            ResourceSnapshot,
            RunStatus,
            SchedulerRun,
            Task,
            TaskStatus,
        )

# Domain Model Spec

## Purpose
Define canonical data structures for agents, conversations, tasks, artifacts, messages/events, scheduler runs, and system resource snapshots.

## Design Goals
- Fast local performance.
- Deterministic resume behavior.
- Clear ownership and lifecycle state.
- Easy AI/human implementation handoff.

## Storage Strategy
- Primary: SQLite (WAL mode) for operational state and indexed queries.
- Secondary: JSONL append logs for transcript/debug/audit export.

## Enum Definitions
## Provider
- `codex`
- `claude`
- `gemini`
- `ollama`

## AgentRole
- `worker`
- `coordinator`
- `moderator`

## AgentStatus
- `idle`
- `running`
- `blocked`
- `offline`

## ConversationState
- `debate`
- `execution_planning`
- `autonomous_work`
- `needs_user_input`
- `completed`
- `failed`
- `queued`

## Phase
- `design_debate`
- `tdd_planning`
- `implementation`
- `integration`
- `docs`
- `merge`

## GateStatus
- `open`
- `satisfied`
- `approved`

## TaskStatus
- `todo`
- `in_progress`
- `blocked`
- `done`
- `failed`

## RunStatus
- `queued`
- `running`
- `paused`
- `waiting_resources`
- `done`
- `failed`

## ArtifactType
- `agreement_map`
- `conflict_map`
- `neutral_memo`
- `checkpoint`
- `test_report`
- `decision_log`

## Entity: Agent
## Fields
- `id TEXT PRIMARY KEY`
- `display_name TEXT NOT NULL`
- `provider TEXT NOT NULL`
- `model TEXT NOT NULL`
- `personality_key TEXT`
- `role TEXT NOT NULL`
- `status TEXT NOT NULL`
- `session_id TEXT` (optional provider conversation id)
- `capabilities_json TEXT NOT NULL` (JSON array/object)
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

## Notes
- `session_id` is optional optimization only.
- `display_name` is user-facing (e.g. `Codex Reviewer`).

## Entity: Conversation
## Fields
- `id TEXT PRIMARY KEY`
- `title TEXT NOT NULL`
- `project_path TEXT NOT NULL`
- `state TEXT NOT NULL`
- `phase TEXT NOT NULL`
- `gate_status TEXT NOT NULL`
- `priority INTEGER NOT NULL DEFAULT 100`
- `active INTEGER NOT NULL DEFAULT 0`
- `summary_snapshot TEXT` (short cached summary)
- `latest_artifact_id TEXT`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`
- `deleted_at TEXT` (soft delete)

## Notes
- Conversations are long-lived workspaces, not disposable chat threads.

## Entity: ConversationAgent
(join table for per-conversation agent configuration)

## Fields
- `id TEXT PRIMARY KEY`
- `conversation_id TEXT NOT NULL`
- `agent_id TEXT NOT NULL`
- `turn_order INTEGER NOT NULL`
- `enabled INTEGER NOT NULL DEFAULT 1`
- `permission_profile TEXT NOT NULL`
- `is_merge_coordinator INTEGER NOT NULL DEFAULT 0`
- `created_at TEXT NOT NULL`

## Constraints
- Exactly one coordinator per active conversation in autonomous mode.

## Entity: Task
## Fields
- `id TEXT PRIMARY KEY`
- `conversation_id TEXT NOT NULL`
- `title TEXT NOT NULL`
- `spec_json TEXT NOT NULL`
- `status TEXT NOT NULL`
- `priority INTEGER NOT NULL DEFAULT 100`
- `owner_agent_id TEXT`
- `depends_on_json TEXT NOT NULL DEFAULT '[]'`
- `started_at TEXT`
- `finished_at TEXT`
- `result_summary TEXT`
- `evidence_json TEXT NOT NULL DEFAULT '[]'`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

## Notes
- Supports division-of-labor and dependency-aware continuation when clarifications block one branch.

## Entity: Artifact
## Fields
- `id TEXT PRIMARY KEY`
- `conversation_id TEXT NOT NULL`
- `batch_id TEXT`
- `type TEXT NOT NULL`
- `payload_json TEXT NOT NULL`
- `created_at TEXT NOT NULL`

## Notes
- Stores agreement/conflict/neutral memo/checkpoints for smart resume.

## Entity: MessageEvent
## Fields
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `conversation_id TEXT NOT NULL`
- `event_id TEXT NOT NULL UNIQUE`
- `source_type TEXT NOT NULL` (`user|agent|system`)
- `source_id TEXT`
- `text TEXT NOT NULL`
- `event_type TEXT NOT NULL`
- `metadata_json TEXT NOT NULL DEFAULT '{}'`
- `created_at TEXT NOT NULL`

## Notes
- Serves chat stream and event timeline.

## Entity: SchedulerRun
## Fields
- `id TEXT PRIMARY KEY`
- `conversation_id TEXT NOT NULL`
- `status TEXT NOT NULL`
- `batch_size INTEGER NOT NULL`
- `reason TEXT`
- `started_at TEXT`
- `ended_at TEXT`
- `created_at TEXT NOT NULL`

## Notes
- Tracks autonomous/background execution lifecycle.

## Entity: ResourceSnapshot
## Fields
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `captured_at TEXT NOT NULL`
- `cpu_load_1m REAL NOT NULL`
- `ram_used_mb INTEGER NOT NULL`
- `ram_total_mb INTEGER NOT NULL`
- `gpu_json TEXT NOT NULL DEFAULT '[]'`
- `agent_capacity_available INTEGER NOT NULL`

## Notes
- Used by auto-throttle scheduler.

## Recommended Indexes
- `conversation(updated_at DESC)`
- `conversation(state, priority, updated_at DESC)`
- `task(conversation_id, status, priority)`
- `message_event(conversation_id, id)`
- `artifact(conversation_id, created_at DESC)`
- `scheduler_run(conversation_id, status, created_at DESC)`

## SQL Baseline (SQLite)
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS agent (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  personality_key TEXT,
  role TEXT NOT NULL,
  status TEXT NOT NULL,
  session_id TEXT,
  capabilities_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  project_path TEXT NOT NULL,
  state TEXT NOT NULL,
  phase TEXT NOT NULL,
  gate_status TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 100,
  active INTEGER NOT NULL DEFAULT 0,
  summary_snapshot TEXT,
  latest_artifact_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS conversation_agent (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  turn_order INTEGER NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  permission_profile TEXT NOT NULL,
  is_merge_coordinator INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  title TEXT NOT NULL,
  spec_json TEXT NOT NULL,
  status TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 100,
  owner_agent_id TEXT,
  depends_on_json TEXT NOT NULL DEFAULT '[]',
  started_at TEXT,
  finished_at TEXT,
  result_summary TEXT,
  evidence_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  batch_id TEXT,
  type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS message_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  event_id TEXT NOT NULL UNIQUE,
  source_type TEXT NOT NULL,
  source_id TEXT,
  text TEXT NOT NULL,
  event_type TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scheduler_run (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  status TEXT NOT NULL,
  batch_size INTEGER NOT NULL,
  reason TEXT,
  started_at TEXT,
  ended_at TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_snapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  captured_at TEXT NOT NULL,
  cpu_load_1m REAL NOT NULL,
  ram_used_mb INTEGER NOT NULL,
  ram_total_mb INTEGER NOT NULL,
  gpu_json TEXT NOT NULL DEFAULT '[]',
  agent_capacity_available INTEGER NOT NULL
);
```

## JSONL Companion Logs
- `data/transcripts/<conversation_id>.jsonl`
- `data/audit/scheduler.jsonl`

## Glue Logic Requirements
- Repository layer maps DB rows <-> domain structs.
- Resume builder consumes checkpoint + summary + recent message window.
- Scheduler consumes `resource_snapshot` and live runs.

## Acceptance Criteria
- Domain model supports:
- multi-conversation background execution,
- token-efficient resume with or without provider session IDs,
- task division and merge coordination,
- deterministic status/notification behavior.

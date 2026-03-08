-- Agent Orchestrator Web - SQLite Schema v1
-- DATA-001: Core persistence tables for conversations, agents, tasks, runs, checkpoints.

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
  sort_order INTEGER NOT NULL DEFAULT 0,
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
  conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
  turn_order INTEGER NOT NULL DEFAULT 0,
  enabled INTEGER NOT NULL DEFAULT 1,
  permission_profile TEXT NOT NULL,
  is_merge_coordinator INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  UNIQUE (conversation_id, agent_id)
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

CREATE TABLE IF NOT EXISTS merge_queue (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
  task_id TEXT NOT NULL REFERENCES task(id) ON DELETE CASCADE,
  pr_number INTEGER,
  pr_url TEXT,
  pr_branch TEXT,
  author_agent_id TEXT NOT NULL REFERENCES agent(id) ON DELETE CASCADE,
  reviewer_agent_id TEXT,
  position INTEGER,
  status TEXT NOT NULL,
  queued_at TEXT,
  merged_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Recommended indexes from domain model spec
CREATE INDEX IF NOT EXISTS idx_conversation_updated_at
  ON conversation(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_state_priority
  ON conversation(state, priority, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_task_conversation_status
  ON task(conversation_id, status, priority);

CREATE INDEX IF NOT EXISTS idx_message_event_conversation
  ON message_event(conversation_id, id);

CREATE INDEX IF NOT EXISTS idx_artifact_conversation_created
  ON artifact(conversation_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_scheduler_run_conversation_status
  ON scheduler_run(conversation_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_merge_queue_conversation
  ON merge_queue(conversation_id, status);

CREATE INDEX IF NOT EXISTS idx_merge_queue_status_position
  ON merge_queue(status, position);

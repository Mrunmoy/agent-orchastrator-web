# Agent Orchestrator Web

[![CI](https://github.com/Mrunmoy/agent-orchastrator-web/actions/workflows/ci.yml/badge.svg)](https://github.com/Mrunmoy/agent-orchastrator-web/actions/workflows/ci.yml)

LAN-accessible, CLI-native multi-agent orchestration workspace.

## Toolchain
This project uses **Nix** for reproducible development.

```bash
nix develop
```

The dev shell now bootstraps frontend dependencies automatically (runs `npm ci --prefix frontend` if `frontend/node_modules` is missing).
If frontend tests still fail with `vitest: not found`, run:
```bash
npm ci --prefix frontend
```

Optional:
```bash
direnv allow
```

## Step-By-Step Runbook

### 1) Enter dev environment
```bash
cd /home/mrumoy/sandbox/agent-orchestrator-web
nix develop
```

### 2) Start local UI mock and checks
```bash
make serve      # http://localhost:8080
make test-ui
make verify
```

### 3) Generate manager handoff packets
```bash
make handoff-packs
```
Kickoff docs:
- `docs/handoff/claude-code/KICKOFF.md`
- `docs/handoff/codex-code/KICKOFF.md`

### 4) Create task worktree by task ID
Preferred flow is task-driven worktree creation:
```bash
make task-worktree TASK_ID=UI-001 PREFIX=claude
make task-worktree TASK_ID=ORCH-001 PREFIX=claude
make task-worktree TASK_ID=DATA-001 PREFIX=claude
```

This creates:
- branch: `claude/<task-slug>`
- worktree: `../agent-orchestrator-worktrees/<task-slug>`
- context file: `.agent-context.md` inside the worktree

### 4.1) Recommended first parallel batch (real tasks)
Start these first:
```bash
# Worker 1 (Claude): backend foundation
make task-worktree TASK_ID=SETUP-001 PREFIX=claude

# Worker 2 (Codex): frontend foundation
make task-worktree TASK_ID=SETUP-002 PREFIX=codex

# Worker 3 (Claude): first backend adapter (starts after SETUP-001 is ready)
make task-worktree TASK_ID=ADPT-001 PREFIX=claude
```

Worktree paths created:
```bash
/home/mrumoy/sandbox/agent-orchestrator-worktrees/setup-backend-layout
/home/mrumoy/sandbox/agent-orchestrator-worktrees/setup-frontend-shell
/home/mrumoy/sandbox/agent-orchestrator-worktrees/adpt-claude-cli
```

### 5) Start CLI agents in each worktree
Example (Claude workers):
```bash
cd /home/mrumoy/sandbox/agent-orchestrator-worktrees/ui-conversations && claude
cd /home/mrumoy/sandbox/agent-orchestrator-worktrees/orch-batch-runner && claude
cd /home/mrumoy/sandbox/agent-orchestrator-worktrees/data-schema-v1 && claude
```

Example (Codex worker on another task):
```bash
make task-worktree TASK_ID=UI-002 PREFIX=codex
cd /home/mrumoy/sandbox/agent-orchestrator-worktrees/ui-chat-timeline && codex
```

### 5.1) Generate task-specific prompt text
From repo root, generate a prompt and paste it into the matching agent terminal:
```bash
make task-prompt TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-setup
make task-prompt TASK_ID=SETUP-002 PREFIX=codex WORKER=codex-setup
make task-prompt TASK_ID=ADPT-001 PREFIX=claude WORKER=claude-adapter
```

### 5.2) One-command task prepare flow (recommended)
Create/sync worktree + write `TASK_PROMPT.md` inside that worktree:
```bash
make task-ready TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-setup
```

Create/sync worktree + write prompt + open interactive shell in that worktree:
```bash
make task-shell TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-setup
```

Then inside that shell:
```bash
claude
# tell claude: read TASK_PROMPT.md and execute
```

### 6) Monitor current parallel state
```bash
make parallel-status
git -C /home/mrumoy/sandbox/agent-orchestrator-web worktree list
```

### 7) Integration policy
- Workers never merge directly to `master`.
- Merge coordinator merges one branch at a time.
- Update `docs/coordination/task-board.md` status: `Todo -> In Progress -> Review -> Done`.

## Common Commands
```bash
make serve
make test-ui
make test-api-conversations
make test-integration
make test-all
make ui-shot
make verify
make parallel-init AGENTS="codex-ui claude-orch ollama-data"
make parallel-status
make handoff-packs
make task-worktree TASK_ID=UI-001 PREFIX=claude
```

## Task Planning Status
- Broad project task list exists in `TASKS.md` (multi-phase backlog).
- Execution-level slices exist in `docs/coordination/task-board.md` + `config/tasks.json`.
- This is a strong **v1 backlog**, but not final. You should keep adding tasks as architecture and implementation evolve.

## Documentation
- `TASKS.md` - task tracker
- `docs/DESIGN.md` - high-level design
- `docs/IMPLEMENTATION_PLAN_V1.md` - sprint implementation plan
- `docs/DEV_ENV.md` - environment and autonomous test loop
- `docs/specs/` - section-by-section implementation contracts
- `docs/coordination/PARALLEL_AGENT_WORKFLOW.md` - multi-agent parallel development workflow
- `docs/coordination/task-board.md` - assign/track independent slices per agent
- `docs/coordination/CROSS_TOOL_HANDOFF.md` - codex-code/claude-code manager protocol
- `docs/handoff/*/KICKOFF.md` - generated manager handoff packets
- `config/tasks.json` - machine-readable task registry (ID -> branch slug/scope)

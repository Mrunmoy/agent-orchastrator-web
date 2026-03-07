# Agent Orchestrator Web

LAN-accessible, CLI-native multi-agent orchestration workspace.

## Toolchain
This project uses **Nix** for reproducible development.

```bash
nix develop
```

Optional:
```bash
direnv allow
```

## Dev Commands
```bash
make serve
make test-ui
make ui-shot
make verify
make parallel-init AGENTS="codex-ui claude-orch ollama-data"
make parallel-status
make handoff-packs
make task-worktree TASK_ID=UI-001 PREFIX=claude
```

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

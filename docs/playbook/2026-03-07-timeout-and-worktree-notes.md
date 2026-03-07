# 2026-03-07 Timeout And Worktree Notes

## Issue 1: Timeout test mismatch in adapter
- Symptom: backend pytest had 1 failure in `TestRunCli.test_run_cli_timeout_kills_process`.
- Cause: timeout exception type handling was inconsistent between mock and adapter catches.
- Fix: catch both `asyncio.TimeoutError` and builtin `TimeoutError` in adapter, and use `asyncio.TimeoutError` in test mock side effect.

## Issue 2: stale worktree shell path
- Symptom: `make task-shell ...` failed with `getcwd: No such file or directory`.
- Cause: command executed from deleted/stale worktree path.
- Recovery:
  1) `cd /home/mrumoy/sandbox/agent-orchestrator-web`
  2) run `make task-shell TASK_ID=... PREFIX=... WORKER=...`

## Preventive Practices
- Always run orchestration `make` targets from repo root.
- Keep generated task prompts in worktree (`TASK_PROMPT.md`) and have worker agent read them verbatim.
- Treat doc updates (design/playbook/saga) as required deliverables for each completed task.

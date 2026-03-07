#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_tasks(tasks_path: Path) -> dict:
    data = json.loads(tasks_path.read_text())
    return {task["id"].upper(): task for task in data.get("tasks", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a ready-to-paste worker prompt by TASK_ID")
    parser.add_argument("task_id", help="Task ID, e.g. SETUP-001")
    parser.add_argument("--repo-root", default=None, help="Repo root (auto-detected by default)")
    parser.add_argument("--tasks-file", default="config/tasks.json", help="Task registry file")
    parser.add_argument("--prefix", default="claude", help="Branch prefix (claude/codex)")
    parser.add_argument("--base-branch", default="master", help="Protected branch name")
    parser.add_argument("--worker-name", default="worker", help="Logical worker label")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parent.parent.resolve()
    tasks_file = (repo_root / args.tasks_file).resolve()

    if not tasks_file.exists():
        raise SystemExit(f"Tasks registry not found: {tasks_file}")

    tasks = load_tasks(tasks_file)
    task_id = args.task_id.upper()
    if task_id not in tasks:
        raise SystemExit(f"Unknown task ID: {task_id}")

    task = tasks[task_id]
    slug = task["slug"]
    branch = f"{args.prefix}/{slug}"
    depends = ", ".join(task.get("depends_on", [])) if task.get("depends_on") else "none"

    prompt = f"""You are {args.worker_name} for task {task_id}.

Read first:
1) .agent-context.md
2) AGENTS.md
3) TASKS.md
4) docs/coordination/task-board.md
5) docs/specs/ (relevant section)

Task details:
- ID: {task_id}
- Epic: {task.get('epic', 'N/A')}
- Priority: {task.get('priority', 'N/A')}
- Title: {task['title']}
- Scope: {task['scope']}
- Depends on: {depends}
- Branch: {branch}

Worktree setup (required):
- From repo root `/home/mrumoy/sandbox/agent-orchestrator-web`, create/sync the task worktree:
  `make task-worktree TASK_ID={task_id} PREFIX={args.prefix}`
- Then switch to:
  `/home/mrumoy/sandbox/agent-orchestrator-worktrees/{slug}`
- Continue all task work from that worktree only.

Execution contract:
- Implement only this task scope.
- Follow TDD: tests first, then implementation, then run tests.
- Keep commits small and descriptive.
- Do not merge to {args.base_branch}.
- If blocked by dependency, stop and report blocker clearly.
- Update project docs as part of completion:
  - design note in `docs/design/`
  - debugging/ops note in `docs/playbook/`
  - milestone update in `docs/saga/`

Board updates required:
- Set owner and status to In Progress when starting.
- Set status to Review when finished.
- Fill branch column with `{branch}`.

Final report format:
1) Changes made
2) Tests run + results
3) Docs updated (design/playbook/saga file paths)
4) Open issues/blockers
5) Next recommended task IDs
"""

    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def git(repo: Path, *args: str) -> str:
    result = run(["git", "-C", str(repo), *args])
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a task-specific worktree from TASK_ID using config/tasks.json"
    )
    parser.add_argument("task_id", help="Task ID, e.g. UI-001")
    parser.add_argument("--repo-root", default=None, help="Repo root (auto-detected by default)")
    parser.add_argument("--tasks-file", default="config/tasks.json", help="Task registry file")
    parser.add_argument("--branch-prefix", default="claude", help="Branch namespace, e.g. claude/codex")
    parser.add_argument("--base-branch", default="master", help="Base branch for new branches")
    parser.add_argument("--worktree-root", default=None, help="Worktree root directory")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parent.parent.resolve()
    tasks_file = (repo_root / args.tasks_file).resolve()
    worktree_root = (
        Path(args.worktree_root).resolve()
        if args.worktree_root
        else (repo_root.parent / "agent-orchestrator-worktrees")
    )

    if not tasks_file.exists():
        raise SystemExit(f"Tasks registry not found: {tasks_file}")

    data = json.loads(tasks_file.read_text())
    tasks = {t["id"]: t for t in data.get("tasks", [])}
    task_id = args.task_id.upper()
    if task_id not in tasks:
        raise SystemExit(f"Unknown task ID: {task_id}")

    task = tasks[task_id]
    slug = task["slug"].strip().lower()
    branch = f"{args.branch_prefix}/{slug}"
    path = (worktree_root / slug).resolve()

    worktree_root.mkdir(parents=True, exist_ok=True)

    try:
        git(repo_root, "fetch", "--all", "--prune")
    except subprocess.CalledProcessError:
        pass

    if (path / ".git").exists() or path.exists() and (path / ".agent-context.md").exists():
        print(f"[skip] worktree exists: {path}")
        print(f"branch={branch}")
        print(f"path={path}")
        return 0

    existing_branches = git(repo_root, "branch", "--list", branch)
    if existing_branches:
        run(["git", "-C", str(repo_root), "worktree", "add", str(path), branch])
    else:
        run(["git", "-C", str(repo_root), "worktree", "add", "-b", branch, str(path), args.base_branch])

    context = f"""# Agent Task Context

Task ID: {task_id}
Title: {task['title']}
Scope: {task['scope']}
Depends On: {', '.join(task['depends_on']) if task['depends_on'] else 'none'}
Default Owner: {task['default_owner']}

Branch: {branch}
Worktree: {path}

Read before coding:
1. AGENTS.md
2. docs/coordination/task-board.md
3. docs/coordination/PARALLEL_AGENT_WORKFLOW.md
4. docs/specs/ (relevant spec)

Execution rules:
- Stay inside assigned scope unless explicitly required.
- Write tests with the implementation.
- Keep commits small and focused.
- Do not merge to {args.base_branch} directly.
"""
    (path / ".agent-context.md").write_text(context)

    print(f"[ok] {task_id} -> {path} ({branch})")
    print(f"task={task_id}")
    print(f"branch={branch}")
    print(f"path={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
